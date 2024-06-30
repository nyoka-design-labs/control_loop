# test_controller.py
import pytest
from unittest.mock import MagicMock, patch
from controllers import create_controller 

@pytest.fixture
def base_controller():
    ctrl, _ = create_controller('fermentation_loop')
    ctrl.update_controller_consts = MagicMock()
    ctrl.update_status = MagicMock()
    return ctrl

@pytest.mark.parametrize(
    "data, trigger_type, start_trig_value, required_readings, start_counter, start_phase_1, trigger_below, expected",
    [
        ({"ph": 6.9}, "ph", 7.0, 5, 0, False, True, False),
        ({"do": 8.1}, "do", 8.0, 1, 0, False, False, True),
        ({"ph": 7.0}, "ph", 7.0, 3, 2, False, True, False),
        ({"do": 5.0}, "do", 6.0, 3, 2, False, True, True),
        ({"do": 5.0}, "do", 6.0, 3, 2, True, True, True),
    ]
)

@pytest.mark.pre_phase_check
def test_pre_phase_check(base_controller, data, trigger_type, start_trig_value, required_readings, start_counter, start_phase_1, trigger_below, expected):
    # Using the public wrapper method to test the private functionality
    result = base_controller.test_pre_phase_check(data, trigger_type, start_trig_value, required_readings, start_counter, start_phase_1, trigger_below)
    assert result == expected
    # Check that update_status was called
    base_controller.update_status.assert_called_once()
    current_value = data[trigger_type]
    # Check if start_phase_1 should have been set to True and verify the call
    should_trigger_update = start_counter + 1 >= required_readings and not start_phase_1 and (
        (trigger_below and current_value < start_trig_value) or 
        (not trigger_below and current_value > start_trig_value)
    )
    if should_trigger_update:
        assert base_controller.update_controller_consts.call_args_list[0] == (('start_phase_1', 'True'),)

@pytest.mark.parametrize(
    "data, trigger_type, start_feed_trig_value, required_readings, feed_counter, start_phase_1, trigger_below, start_feed, expected, expected_calls",
    [
        ({"ph": 6.9}, "ph", 7.0, 3, 0, True, False, False, False, 1),
        ({"do": 8.1}, "do", 8.0, 1, 0, True, False, False, True, 1),
        ({"do": 8.1}, "do", 8.0, 1, 1, True, False, False, True, 1),
        ({"ph": 6.8}, "ph", 7.0, 3, 2, True, False, False, False, 1),
        ({"ph": 6.5}, "ph", 7.0, 3, 2, True, True, False, True, 1),
    ]
)

@pytest.mark.start_feed_check_bool
def test_start_feed_check_bool(base_controller, data, trigger_type, start_feed_trig_value, required_readings, feed_counter, start_phase_1, trigger_below, start_feed, expected, expected_calls):
    result = base_controller.test_start_feed_check_bool(data, trigger_type, start_feed_trig_value, required_readings, feed_counter, start_phase_1, trigger_below, start_feed)
    assert result == expected
    # Verifying update_status is called exactly once per test case
    base_controller.update_status.assert_called_once()

    current_value = data[trigger_type]
    should_trigger_update = feed_counter + 1 >= required_readings and not start_phase_1 and (
        (trigger_below and current_value < start_feed_trig_value) or 
        (not trigger_below and current_value > start_feed_trig_value)
    )

    if should_trigger_update:
        print(f"args list for update_controller_const: {base_controller.update_controller_consts.call_args_list}")
        assert base_controller.update_controller_consts.call_args_list[1] == (('start_phase_1', 'True'),)


@pytest.mark.parametrize(
    "derivs, der_positive, expected, expected_feed, mock_derivative, is_positive",
    [
        ([-0.1, 0.2, 0.3], True, True, True, 0.4, True),
        ([-0.1, -0.2, -0.3], False, True, True, -0.4, True),
        ([0.1, 0.2, 0.3], False, False, False, 0.4, False),
        ([0.1, -0.2, -0.3], True, False, False, -0.4, False),
        ([0.1, 0.2], True, False, True, 0.3, True)  # Not enough data points
    ]
)

@pytest.mark.start_feed_check_der
def test_start_feed_check_der(base_controller, derivs, der_positive, expected, expected_feed, mock_derivative, is_positive):
    with patch('controllers.calculate_derivative', return_value=mock_derivative) as mock_calc_der, \
         patch('controllers.isDerPositive', return_value=is_positive) as mock_is_der_pos:
        result = base_controller.test_start_feed_check_der('do', 4, derivs, "dummy", required_readings=3, der_positive=der_positive)
        assert result == expected_feed
        assert mock_calc_der.called_once_with('do', "dummy", 3)
        
        if len(derivs) >= 3:  # Only check if enough data points
            assert mock_is_der_pos.called_once_with(derivs, 3)

        base_controller.update_status.assert_called_once()
        base_controller.update_controller_consts.assert_any_call("feed_counter", 5)
        if expected:
            base_controller.update_controller_consts.assert_any_call("start_feed", "True")
        neg_factor = 1 if der_positive else -1
        inverted_derivs = [x * neg_factor for x in derivs]
        base_controller.update_controller_consts.assert_any_call("derivs", inverted_derivs)

@pytest.fixture
def pump_controller(base_controller):
    base_controller.pump_control = MagicMock()
    base_controller.pumps = {'test_pump': MagicMock()}
    return base_controller

@pytest.mark.parametrize(
    "current_value, pump_name, feed_trigger_type, feed_trigger_upper_sp, feed_trigger_lower_sp, trigger_above, expected_activation",
    [
        (10, 'test_pump', 'ph', 9, 5, True, True),  # Exceeds upper, should activate
        (4, 'test_pump', 'ph', 9, 5, True, False),  # Below lower, should deactivate
        (4, 'test_pump', 'ph', 5, 9, False, True),  # Below lower, should activate when trigger_above is False
        (10, 'test_pump', 'ph', 5, 9, False, False) # Exceeds upper, should deactivate when trigger_above is False
    ]
)

@pytest.mark.control_pump_activation
def test_control_pump_activation(pump_controller, current_value, pump_name, feed_trigger_type, feed_trigger_upper_sp, feed_trigger_lower_sp, trigger_above, expected_activation):
    # with patch('controllers.setup_logger.info') as mock_logger_info:
    # Set up data
    data = {feed_trigger_type: current_value}
    pump_controller.test_control_pump_activation(data, pump_name, feed_trigger_type, feed_trigger_upper_sp, feed_trigger_lower_sp, trigger_above)

    # Assert pump control behavior
    if expected_activation:
        pump_controller.pump_control.assert_called_once_with(pump_controller.pumps[pump_name].control(True))
        # mock_logger_info.assert_called_with(f"{pump_name} pump on")
    else:
        pump_controller.pump_control.assert_called_once_with(pump_controller.pumps[pump_name].control(False))
        # mock_logger_info.assert_called_with(f"{pump_name} pump off")

    # Assert status update
    pump_controller.update_status.assert_called_once()