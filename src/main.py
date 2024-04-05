from controller import Controller


def main():
    controller = Controller()

    try:
        controller.loop()
    except KeyboardInterrupt:
        print("Program terminated")

if __name__ == '__main__':
    main()