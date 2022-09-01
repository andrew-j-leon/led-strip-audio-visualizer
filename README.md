# LED Strip Audio Visualizer

This project visualizes the audio going into your computer's **default audio input device** (such as a microphone) as a colorful [spectrogram](https://en.wikipedia.org/wiki/Spectrogram) displayed on either a **strip of individually addressable LEDs** (specifically WS2812B LEDs) or through a **GUI**.

[Here is a YouTube video demonstrating what it can do on a WS2812B LED strip.](https://youtu.be/pxNwhaRPMZ4)

# Before Getting Started

I recommend reading through the following resources to get an understanding of the technologies you will be using.

- [This video](https://www.youtube.com/watch?v=QnvircC22hU&ab_channel=TheHookUp) provides an overview of the different types of individually addressable LED strips that are available (as well as their strengths and weaknesses). The type that this project was built using is the **WS2812B** variety.

- We will use a microcontroller called an **Arduino** to control the LED strip. [Arduino's getting started guide](https://www.arduino.cc/en/Guide) is a great resource to read through.

- Adafruit has a [great guide on their flavor of WS2812B LED strips, called NeoPixels](https://learn.adafruit.com/adafruit-neopixel-uberguide/the-magic-of-neopixels). The guide also provides instructions on **how to connect your Arduino to the LED strip**.

# Installation Guide

> **Note:** This section assumes you want to visualize audio on an LED strip. If you ***only*** want to use the GUI audio visualizer, you just need to (1) download this repository, (2) install Python, and (3) pip install the 3rd party requirements listed in **python/requirements.txt**.

## Step 1: Purchase your Hardware

You can purchase the **WS2812B LED strips** from [Adafruit's official website](https://www.adafruit.com/) or through [Amazon](https://www.amazon.com/s?k=WS2812B+LED+strip&crid=2KST0AJ2HLCX0&sprefix=ws2812b+led+strip%2Caps%2C161&ref=nb_sb_noss_1).

> **Note:** On Adafruit's website, WS2812B LED strips are called "NeoPixels". As long as the LED specification is WS2812B, the LED strip should work with this project. **Specifications other than WS2812B** ***may*** work, but you may need to edit the **arduino/main/main.ino** sketch to get them to work. It all depends on what the [FastLed NeoPixel library](https://github.com/dmadison/FastLED_NeoPixel) (which is the library my Arduino sketch uses to control the LED strip) supports.

The **Arduino** is the microcrontroller which will control the LED strip(s). You can purchase an Arduino from the [official website](https://www.arduino.cc/) or from [Amazon](https://www.amazon.com/arduino/s?k=arduino).

> **Note:** In order to control the LED strips, this projects uses a 3rd party Arduino library called **FastLED_NeoPixel**. Internally, this library requires 3 bytes for each LED strip in order to store each LED's RGB color. ***Make sure the Arduino you purchase has enough memory to store the data for each LED!*** This project was created with an Arduino Uno, so that would be a good version to purchase if you don't know which to pick. The most recent Arduino Uno version would (probably) be best, but the version I used is the Arduino Uno WiFi Rev2 (which is like a regular Arduino Uno, but with built in WiFi and bluetooth capabilities).

You will also need an **A-Male to B-Male USB cord** to connect (and power) the Arduino to your PC.

You will also need a **power supply** (to power your LED strip), along with a **resistor**, **capacitor**, and some **jumper wire cables** to safely connect the LED strip to your Arduino. Read through Adafruit's [guide on NeoPixels (WS2812B LED strips)](https://learn.adafruit.com/adafruit-neopixel-uberguide/the-magic-of-neopixels) to pick out the correct parts. Pay extra close attention to the guide's [basic connections](https://learn.adafruit.com/adafruit-neopixel-uberguide/basic-connections) section, as you will need this knowledge to connect your LED strip to your Arduino.

## Step 2: Download this Repository

Either download this project as a zip file and extract it or use git clone:

    git clone https://github.com/andrew-j-leon/led-strip-audio-visualizer.git

## Step 3: Install Python

This project was developed using **Python 3.10.4**.

I recommend installing the latest version of Python from its [official website](https://www.python.org/downloads/).

## Step 4: Install 3rd Party Python Dependencies

You can install the necessary 3rd party Python dependencies by running the following command:

    python -m pip install -r python/requirements.txt

> **Note:** If you have trouble installing the PyAudio dependencies, you may need to download it from the [official website](https://people.csail.mit.edu/hubert/pyaudio/). On Windows, you can also try installing PyAudio using [PipWin](https://pypi.org/project/pipwin/) instead of pip.

## Step 5: Connect the Arduino to the LED Strip

If you haven't already, make sure you read through Adafruit's [guide on NeoPixels (WS2812B LED strips)](https://learn.adafruit.com/adafruit-neopixel-uberguide/the-magic-of-neopixels). In particular, the [basic connections](https://learn.adafruit.com/adafruit-neopixel-uberguide/basic-connections) section will tell you how to connect your Arduino to the LED strip.

Connect your arduino to the LED strip using Pin 7 as the data pin.

> **Note:** You can change this pin number by changing the `PIN_NUMBER` global variable in the **arduino/main/main.ino** sketch.

## Step 6: Update the NUMBER_OF_LEDS Global Variable in main.ino

In the **arduino/main/main.ino** sketch, set the `NUMBER_OF_LEDS` global variable equal to the number of LEDs on your LED strip.

## Step 7: Upload the main.ino Arduino Sketch

First, follow [Arduino's getting started guide](https://www.arduino.cc/en/Guide) in order to learn how to use the Arduino IDE to:

1. Upload sketches onto your Arduino device.
2. Download 3rd party libraries.

Next, using the Arduino IDE, download the [FastLed NeoPixel library](https://github.com/dmadison/FastLED_NeoPixel).

Finally, upload the **arduino/main/main.ino** sketch to your Arduino.

## Step 8: Run the Python Scripts and set the Correct Serial Settings

You should now be able to run **python/main.py** to start the program.

Do so now. You should see a GUI appear.

Click the **Settings button** and make sure you set the following values correctly:

1. `Port:` Set this to the USB port your Arduino is connected to (on Windows, this may be COM3; on Ubuntu, it may be /dev/ttyACM0). The correct port number should be shown in the Arduino IDE.

2. `Baudrate:` Set this to 1000000.

> **Note:** If you want to use a different baudrate, you can edit the **arduino/main/main.ino** sketch's `SERIAL_BAUD_RATE` global variable. If you do so, don't forget to re-upload the sketch!

Save your settings.

Close the settings page.

Back on the main page, select "Serial LED Strip" for the `LED Strip Type`.

Click Play. The program will now listen in on your computer's default input device and update the LED strip accordingly.

> **Tip:** On **Windows** machines, you can follow [this tutorial](https://www.howtogeek.com/364369/how-to-record-your-pcs-audio-with-vb-cable/) to redirect your speaker's audio to your default input device. On **Linux**, you can use [this tutorial](https://www.kirsle.net/redirect-audio-out-to-mic-in-linux) to do something similar. You can now play music on your computer and the LEDs will light up in response!