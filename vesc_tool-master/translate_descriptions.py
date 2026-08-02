#!/usr/bin/env python3
"""
Translate <description> elements in parameters_mcconf.xml and parameters_appconf.xml
across all version directories under res/config/.
Uses pattern-based substring replacement on the HTML description text.
Only modifies descriptions that contain matching English patterns.
"""

import os
import sys
import xml.etree.ElementTree as ET

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "config")

DESCRIPTION_PATTERNS = {
    # ===== PWM Mode =====
    "The PWM mode to use for BLDC motors.":
        "BLDC \u7535\u673a\u4f7f\u7528\u7684 PWM \u6a21\u5f0f\u3002",
    "Synchronous is the most tested and recommended mode.":
        "\u540c\u6b65\u6a21\u5f0f\u662f\u6d4b\u8bd5\u6700\u5145\u5206\u3001\u63a8\u8350\u4f7f\u7528\u7684\u6a21\u5f0f\u3002",
    "The others are likely to cause problems.":
        "\u5176\u4ed6\u6a21\u5f0f\u53ef\u80fd\u5bfc\u81f4\u95ee\u9898\u3002",

    # ===== Commutation Mode =====
    "The commutation mode to use for the motor.":
        "\u7535\u673a\u4f7f\u7528\u7684\u6362\u5411\u6a21\u5f0f\u3002",
    "Integrate uses an integrator for delay compensation.":
        "\u79ef\u5206\u6a21\u5f0f\u4f7f\u7528\u79ef\u5206\u5668\u8fdb\u884c\u5ef6\u8fdf\u8865\u507f\u3002",
    "Delay uses a delay for delay compensation.":
        "\u5ef6\u8fdf\u6a21\u5f0f\u4f7f\u7528\u5ef6\u8fdf\u8fdb\u884c\u5ef6\u8fdf\u8865\u507f\u3002",

    # ===== General =====
    "Refer to the supported hardware page on the VESC Project website for details.":
        "\u8be6\u60c5\u8bf7\u53c2\u9605 VESC \u9879\u76ee\u7f51\u7ad9\u4e0a\u7684\u652f\u6301\u786c\u4ef6\u9875\u9762\u3002",

    # ===== Motor Type =====
    "The motor type. Options are:":
        "\u7535\u673a\u7c7b\u578b\u3002\u9009\u9879\uff1a",
    "BLDC: Brushless DC motor. This is the most common type for electric skateboards, ebikes and similar.":
        "BLDC\uff1a\u65e0\u5237\u76f4\u6d41\u7535\u673a\u3002\u8fd9\u662f\u7535\u52a8\u6ed1\u677f\u3001\u7535\u52a8\u81ea\u884c\u8f66\u7b49\u6700\u5e38\u89c1\u7684\u7c7b\u578b\u3002",
    "DC: Brushed DC motor. Can also be used for some applications.":
        "DC\uff1a\u6709\u5237\u76f4\u6d41\u7535\u673a\u3002\u4e5f\u53ef\u7528\u4e8e\u67d0\u4e9b\u5e94\u7528\u3002",
    "FOC: Field Oriented Control. This is the most advanced and efficient mode, but requires more tuning.":
        "FOC\uff1a\u78c1\u573a\u5b9a\u5411\u63a7\u5236\u3002\u8fd9\u662f\u6700\u5148\u8fdb\u3001\u6700\u9ad8\u6548\u7684\u6a21\u5f0f\uff0c\u4f46\u9700\u8981\u66f4\u591a\u8c03\u8bd5\u3002",

    # ===== Sensor Port Mode =====
    "Select which sensor port mode to use.":
        "\u9009\u62e9\u4f7f\u7528\u7684\u4f20\u611f\u5668\u7aef\u53e3\u6a21\u5f0f\u3002",
    "Hall Sensors: Use hall sensors.":
        "\u970d\u5c14\u4f20\u611f\u5668\uff1a\u4f7f\u7528\u970d\u5c14\u4f20\u611f\u5668\u3002",
    "ABI Encoder: Use an ABI encoder.":
        "ABI \u7f16\u7801\u5668\uff1a\u4f7f\u7528 ABI \u7f16\u7801\u5668\u3002",
    "AS5047 Encoder: Use an AS5047 encoder (SPI).":
        "AS5047 \u7f16\u7801\u5668\uff1a\u4f7f\u7528 AS5047 \u7f16\u7801\u5668\uff08SPI\uff09\u3002",
    "AD2S1205 Resolver: Use an AD2S1205 resolver.":
        "AD2S1205 \u65cb\u8f6c\u53d8\u538b\u5668\uff1a\u4f7f\u7528 AD2S1205 \u65cb\u8f6c\u53d8\u538b\u5668\u3002",
    "Sin/Cos Encoder: Use a Sin/Cos encoder.":
        "\u6b63\u4f59\u5f26\u7f16\u7801\u5668\uff1a\u4f7f\u7528\u6b63\u4f59\u5f26\u7f16\u7801\u5668\u3002",
    "TS5700N8501 Encoder: Use a TS5700N8501 encoder.":
        "TS5700N8501 \u7f16\u7801\u5668\uff1a\u4f7f\u7528 TS5700N8501 \u7f16\u7801\u5668\u3002",
    "MT6816 Encoder: Use an MT6816 encoder (SPI).":
        "MT6816 \u7f16\u7801\u5668\uff1a\u4f7f\u7528 MT6816 \u7f16\u7801\u5668\uff08SPI\uff09\u3002",
    "AS5X47U Encoder: Use an AS5X47U encoder (SPI).":
        "AS5X47U \u7f16\u7801\u5668\uff1a\u4f7f\u7528 AS5X47U \u7f16\u7801\u5668\uff08SPI\uff09\u3002",
    "BISSC Encoder: Use a BISSC encoder (SPI).":
        "BISSC \u7f16\u7801\u5668\uff1a\u4f7f\u7528 BISSC \u7f16\u7801\u5668\uff08SPI\uff09\u3002",
    "TLE5012 Encoder: Use a TLE5012 encoder.":
        "TLE5012 \u7f16\u7801\u5668\uff1a\u4f7f\u7528 TLE5012 \u7f16\u7801\u5668\u3002",
    "Custom Encoder: Use a custom encoder.":
        "\u81ea\u5b9a\u4e49\u7f16\u7801\u5668\uff1a\u4f7f\u7528\u81ea\u5b9a\u4e49\u7f16\u7801\u5668\u3002",

    # ===== Sensor Mode =====
    "The sensor mode determines which type of sensors are used for commutation.":
        "\u4f20\u611f\u5668\u6a21\u5f0f\u51b3\u5b9a\u6362\u5411\u4f7f\u7528\u54ea\u79cd\u4f20\u611f\u5668\u7c7b\u578b\u3002",
    "Sensorless: No sensors are used. The motor position is estimated from the back-EMF.":
        "\u65e0\u611f\uff1a\u4e0d\u4f7f\u7528\u4f20\u611f\u5668\u3002\u901a\u8fc7\u53cd\u7535\u52a8\u52bf\u4f30\u7b97\u7535\u673a\u4f4d\u7f6e\u3002",
    "Sensored: Hall sensors are used for commutation.":
        "\u6709\u611f\uff1a\u4f7f\u7528\u970d\u5c14\u4f20\u611f\u5668\u8fdb\u884c\u6362\u5411\u3002",
    "Encoder: An encoder is used for commutation.":
        "\u7f16\u7801\u5668\uff1a\u4f7f\u7528\u7f16\u7801\u5668\u8fdb\u884c\u6362\u5411\u3002",
    "HFI: High Frequency Injection is used for sensorless control at low speeds.":
        "HFI\uff1a\u9ad8\u9891\u6ce8\u5165\u7528\u4e8e\u4f4e\u901f\u65e0\u611f\u63a7\u5236\u3002",
    "Select the sensor mode for the motor.":
        "\u9009\u62e9\u7535\u673a\u7684\u4f20\u611f\u5668\u6a21\u5f0f\u3002",

    # ===== Current Limits =====
    "The absolute maximum current is used as a hard current limit.":
        "\u7edd\u5bf9\u6700\u5927\u7535\u6d41\u7528\u4f5c\u786c\u7535\u6d41\u9650\u5236\u3002",
    "This setting sets a limit that will cause an overcurrent fault if exceeded.":
        "\u6b64\u8bbe\u7f6e\u8bbe\u5b9a\u7684\u9650\u5236\u5982\u679c\u88ab\u8d85\u8fc7\u5c06\u5bfc\u81f4\u8fc7\u6d41\u6545\u969c\u3002",
    "It is recommended to set this at least 1.5 times higher than the motor current limit.":
        "\u5efa\u8bae\u5c06\u5176\u8bbe\u7f6e\u4e3a\u7535\u673a\u7535\u6d41\u9650\u5236\u7684\u81f3\u5c11 1.5 \u500d\u3002",
    "The maximum motor current.":
        "\u6700\u5927\u7535\u673a\u7535\u6d41\u3002",
    "The minimum motor current (negative = braking).":
        "\u6700\u5c0f\u7535\u673a\u7535\u6d41\uff08\u8d1f\u6570 = \u5236\u52a8\uff09\u3002",
    "The maximum current from the battery.":
        "\u7535\u6c60\u6700\u5927\u7535\u6d41\u3002",
    "The minimum current from the battery (negative = regen).":
        "\u7535\u6c60\u6700\u5c0f\u7535\u6d41\uff08\u8d1f\u6570 = \u56de\u751f\uff09\u3002",
    "This function reduces the motor current as the mapped input current approaches the limit.":
        "\u6b64\u529f\u80fd\u5728\u6620\u5c04\u7684\u8f93\u5165\u7535\u6d41\u63a5\u8fd1\u9650\u5236\u65f6\u964d\u4f4e\u7535\u673a\u7535\u6d41\u3002",
    "The start of the input current ramp down is determined by this parameter.":
        "\u6b64\u53c2\u6570\u786e\u5b9a\u8f93\u5165\u7535\u6d41\u5f00\u59cb\u964d\u4f4e\u7684\u8d77\u59cb\u70b9\u3002",
    "A lower value means it will start reducing the motor current earlier.":
        "\u8f83\u4f4e\u7684\u503c\u610f\u5473\u7740\u4f1a\u66f4\u65e9\u5f00\u59cb\u964d\u4f4e\u7535\u673a\u7535\u6d41\u3002",
    "A filter on the mapped input current can be used to smooth out the current reduction.":
        "\u53ef\u4ee5\u5bf9\u6620\u5c04\u7684\u8f93\u5165\u7535\u6d41\u4f7f\u7528\u6ee4\u6ce2\u5668\u6765\u5e73\u6ed1\u7535\u6d41\u964d\u4f4e\u3002",
    "The motor current is scaled from 0 to 1 for each profile.":
        "\u6bcf\u4e2a\u914d\u7f6e\u6587\u4ef6\u7684\u7535\u673a\u7535\u6d41\u4ece 0 \u5230 1 \u7f29\u653e\u3002",
    "Use the profiles page to set up custom current scales.":
        "\u4f7f\u7528\u914d\u7f6e\u6587\u4ef6\u9875\u9762\u8bbe\u7f6e\u81ea\u5b9a\u4e49\u7535\u6d41\u6bd4\u4f8b\u3002",

    # ===== Slow ABS Current =====
    "If enabled, the absolute current limit will use a slow filter.":
        "\u5982\u679c\u542f\u7528\uff0c\u7edd\u5bf9\u7535\u6d41\u9650\u5236\u5c06\u4f7f\u7528\u6162\u901f\u6ee4\u6ce2\u5668\u3002",
    "This is NOT recommended as it increases the chance of permanent damage to the controller.":
        "\u4e0d\u5efa\u8bae\u4f7f\u7528\uff0c\u56e0\u4e3a\u8fd9\u4f1a\u589e\u52a0\u6c38\u4e45\u635f\u574f\u63a7\u5236\u5668\u7684\u98ce\u9669\u3002",

    # ===== Temperature Limits =====
    "The MOSFET temperature at which the motor current starts to be reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u673a\u7535\u6d41\u7684 MOSFET \u6e29\u5ea6\u3002",
    "The MOSFET temperature at which the motor current is reduced to 0.":
        "\u7535\u673a\u7535\u6d41\u964d\u81f3 0 \u7684 MOSFET \u6e29\u5ea6\u3002",
    "The motor temperature at which the motor current starts to be reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u673a\u7535\u6d41\u7684\u7535\u673a\u6e29\u5ea6\u3002",
    "The motor temperature at which the motor current is reduced to 0.":
        "\u7535\u673a\u7535\u6d41\u964d\u81f3 0 \u7684\u7535\u673a\u6e29\u5ea6\u3002",
    "The acceleration and deceleration rate for temperature controlled current reduction.":
        "\u6e29\u5ea6\u63a7\u5236\u7535\u6d41\u964d\u4f4e\u7684\u52a0\u901f\u548c\u51cf\u901f\u901f\u7387\u3002",

    # ===== Voltage Limits =====
    "The battery voltage where the motor current starts to be reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u673a\u7535\u6d41\u7684\u7535\u6c60\u7535\u538b\u3002",
    "The battery voltage where the motor current is reduced to 0.":
        "\u7535\u673a\u7535\u6d41\u964d\u81f3 0 \u7684\u7535\u6c60\u7535\u538b\u3002",
    "The battery voltage where the regen current starts to be reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u56de\u751f\u7535\u6d41\u7684\u7535\u6c60\u7535\u538b\u3002",
    "The battery voltage where the regen current is reduced to 0.":
        "\u56de\u751f\u7535\u6d41\u964d\u81f3 0 \u7684\u7535\u6c60\u7535\u538b\u3002",
    "This is useful for preventing the battery from over-discharging.":
        "\u8fd9\u5bf9\u4e8e\u9632\u6b62\u7535\u6c60\u8fc7\u5ea6\u653e\u7535\u5f88\u6709\u7528\u3002",
    "A filter constant for the battery voltage measurement.":
        "\u7535\u6c60\u7535\u538b\u6d4b\u91cf\u7684\u6ee4\u6ce2\u5e38\u6570\u3002",

    # ===== RPM/ERPM Limits =====
    "The maximum ERPM (electrical RPM) the motor is allowed to spin at.":
        "\u7535\u673a\u5141\u8bb8\u7684\u6700\u5927 ERPM\uff08\u7535\u6c14\u8f6c\u901f\uff09\u3002",
    "The minimum ERPM the motor is allowed to spin at (negative = reverse).":
        "\u7535\u673a\u5141\u8bb8\u7684\u6700\u5c0f ERPM\uff08\u8d1f\u6570 = \u53cd\u8f6c\uff09\u3002",
    "The ERPM above which the motor can start running (useful for push-start).":
        "\u7535\u673a\u53ef\u4ee5\u5f00\u59cb\u8fd0\u884c\u7684 ERPM \u9608\u503c\uff08\u7528\u4e8e\u63a8\u8f66\u542f\u52a8\uff09\u3002",
    "The ERPM at which the full brake function starts to decrease from maximum.":
        "\u5168\u5239\u8f66\u529f\u80fd\u5f00\u59cb\u4ece\u6700\u5927\u503c\u964d\u4f4e\u7684 ERPM\u3002",
    "The ERPM at which the full brake in current control mode starts to decrease.":
        "\u7535\u6d41\u63a7\u5236\u6a21\u5f0f\u4e0b\u5168\u5239\u8f66\u5f00\u59cb\u964d\u4f4e\u7684 ERPM\u3002",

    # ===== Input Voltage =====
    "The minimum input voltage required for the motor to operate.":
        "\u7535\u673a\u8fd0\u884c\u6240\u9700\u7684\u6700\u5c0f\u8f93\u5165\u7535\u538b\u3002",
    "The maximum input voltage allowed for the motor.":
        "\u7535\u673a\u5141\u8bb8\u7684\u6700\u5927\u8f93\u5165\u7535\u538b\u3002",

    # ===== Duty Cycle =====
    "The minimum duty cycle the motor is allowed to run at.":
        "\u7535\u673a\u5141\u8bb8\u8fd0\u884c\u7684\u6700\u5c0f\u5360\u7a7a\u6bd4\u3002",
    "The maximum duty cycle the motor is allowed to run at.":
        "\u7535\u673a\u5141\u8bb8\u8fd0\u884c\u7684\u6700\u5927\u5360\u7a7a\u6bd4\u3002",
    "The duty cycle at which the motor can start running.":
        "\u7535\u673a\u53ef\u4ee5\u5f00\u59cb\u8fd0\u884c\u7684\u5360\u7a7a\u6bd4\u3002",

    # ===== Power =====
    "The maximum power the motor is allowed to draw from the battery.":
        "\u7535\u673a\u5141\u8bb8\u4ece\u7535\u6c60\u62bd\u53d6\u7684\u6700\u5927\u529f\u7387\u3002",
    "The minimum power the motor is allowed to regen to the battery (negative).":
        "\u7535\u673a\u5141\u8bb8\u56de\u751f\u5230\u7535\u6c60\u7684\u6700\u5c0f\u529f\u7387\uff08\u8d1f\u6570\uff09\u3002",

    # ===== BLDC Sensorless =====
    "The cycle integral limit for sensorless BLDC commutation.":
        "\u65e0\u611f BLDC \u6362\u5411\u7684\u5468\u671f\u79ef\u5206\u9650\u5236\u3002",
    "A lower value gives more torque but less stable starting.":
        "\u8f83\u4f4e\u7684\u503c\u63d0\u4f9b\u66f4\u5927\u626d\u77e9\u4f46\u542f\u52a8\u4e0d\u592a\u7a33\u5b9a\u3002",
    "The minimum sensorless ERPM the motor can run at.":
        "\u7535\u673a\u53ef\u4ee5\u8fd0\u884c\u7684\u6700\u4f4e\u65e0\u611f ERPM\u3002",
    "The BEMF coupling constant for the motor.":
        "\u7535\u673a\u7684 BEMF \u8026\u5408\u5e38\u6570\u3002",

    # ===== Hall Sensors =====
    "The ERPM threshold where hall sensors are used for commutation.":
        "\u4f7f\u7528\u970d\u5c14\u4f20\u611f\u5668\u6362\u5411\u7684 ERPM \u9608\u503c\u3002",
    "Hall sensor interpolation ERPM threshold.":
        "\u970d\u5c14\u4f20\u611f\u5668\u63d2\u503c ERPM \u9608\u503c\u3002",

    # ===== FOC Motor Parameters =====
    "The resistance of the motor windings.":
        "\u7535\u673a\u7ed5\u7ec4\u7535\u963b\u3002",
    "The inductance of the motor windings.":
        "\u7535\u673a\u7ed5\u7ec4\u7535\u611f\u3002",
    "The difference between Ld and Lq inductance.":
        "Ld \u548c Lq \u7535\u611f\u4e4b\u5dee\u3002",
    "The flux linkage of the motor magnets.":
        "\u7535\u673a\u78c1\u94c1\u7684\u78c1\u94fe\u3002",

    # ===== FOC Current Controller =====
    "The proportional gain for the current controllers.":
        "\u7535\u6d41\u63a7\u5236\u5668\u7684\u6bd4\u4f8b\u589e\u76ca\u3002",
    "The integral gain for the current controllers.":
        "\u7535\u6d41\u63a7\u5236\u5668\u7684\u79ef\u5206\u589e\u76ca\u3002",
    "The gain for the position/speed observer.":
        "\u4f4d\u7f6e/\u901f\u5ea6\u89c2\u6d4b\u5668\u7684\u589e\u76ca\u3002",
    "A higher value gives better performance but can cause instability.":
        "\u8f83\u9ad8\u7684\u503c\u63d0\u4f9b\u66f4\u597d\u6027\u80fd\u4f46\u53ef\u80fd\u5bfc\u81f4\u4e0d\u7a33\u5b9a\u3002",
    "A lower value gives more stability but slower response.":
        "\u8f83\u4f4e\u7684\u503c\u63d0\u4f9b\u66f4\u9ad8\u7a33\u5b9a\u6027\u4f46\u54cd\u5e94\u8f83\u6162\u3002",

    # ===== FOC Observer =====
    "The observer type used for sensorless FOC.":
        "\u65e0\u611f FOC \u4f7f\u7528\u7684\u89c2\u6d4b\u5668\u7c7b\u578b\u3002",

    # ===== FOC Openloop / Sensorless =====
    "The ERPM where the motor switches to sensorless mode from openloop.":
        "\u7535\u673a\u4ece\u5f00\u73af\u5207\u6362\u5230\u65e0\u611f\u6a21\u5f0f\u7684 ERPM\u3002",
    "The ERPM where the motor starts transitioning to sensorless mode.":
        "\u7535\u673a\u5f00\u59cb\u8fc7\u6e21\u5230\u65e0\u611f\u6a21\u5f0f\u7684 ERPM\u3002",
    "The time the motor runs in openloop before transitioning to sensorless.":
        "\u7535\u673a\u5728\u8fc7\u6e21\u5230\u65e0\u611f\u4e4b\u524d\u8fd0\u884c\u5728\u5f00\u73af\u7684\u65f6\u95f4\u3002",
    "The boost current in openloop mode to get the motor started.":
        "\u5f00\u73af\u6a21\u5f0f\u4e0b\u542f\u52a8\u7535\u673a\u7684\u589e\u5f3a\u7535\u6d41\u3002",

    # ===== Encoder =====
    "The encoder offset for aligning the encoder with the motor.":
        "\u7f16\u7801\u5668\u4e0e\u7535\u673a\u5bf9\u9f50\u7684\u504f\u79fb\u91cf\u3002",
    "The encoder ratio for gear reduction or multiplication.":
        "\u9f7f\u8f6e\u51cf\u901f\u6216\u500d\u589e\u7684\u7f16\u7801\u5668\u6bd4\u7387\u3002",
    "Invert the encoder direction.":
        "\u53cd\u8f6c\u7f16\u7801\u5668\u65b9\u5411\u3002",

    # ===== FOC Sampling =====
    "The mode for sampling the phase currents.":
        "\u76f8\u4f4d\u7535\u6d41\u91c7\u6837\u6a21\u5f0f\u3002",
    "The sample mode for the motor current controller.":
        "\u7535\u673a\u7535\u6d41\u63a7\u5236\u5668\u7684\u91c7\u6837\u6a21\u5f0f\u3002",

    # ===== FOC Saturation =====
    "The mode for compensating for magnetic saturation.":
        "\u78c1\u9971\u548c\u8865\u507f\u6a21\u5f0f\u3002",
    "The amount of magnetic saturation compensation.":
        "\u78c1\u9971\u548c\u8865\u507f\u91cf\u3002",

    # ===== FOC Temperature Compensation =====
    "Temperature compensation mode for the motor resistance.":
        "\u7535\u673a\u7535\u963b\u7684\u6e29\u5ea6\u8865\u507f\u6a21\u5f0f\u3002",
    "The base temperature for temperature compensation.":
        "\u6e29\u5ea6\u8865\u507f\u7684\u57fa\u51c6\u6e29\u5ea6\u3002",

    # ===== FOC Filter / Decoupling =====
    "A low pass filter for the measured motor currents.":
        "\u6d4b\u91cf\u7535\u673a\u7535\u6d41\u7684\u4f4e\u901a\u6ee4\u6ce2\u5668\u3002",
    "The cross-coupling decoupling mode for FOC.":
        "FOC \u7684\u4ea4\u53c9\u8026\u5408\u89e3\u8026\u6a21\u5f0f\u3002",

    # ===== HFI =====
    "The mode for High Frequency Injection sensorless startup.":
        "\u9ad8\u9891\u6ce8\u5165\u65e0\u611f\u542f\u52a8\u6a21\u5f0f\u3002",
    "The current used for HFI.":
        "HFI \u4f7f\u7528\u7684\u7535\u6d41\u3002",
    "The voltage used at startup for HFI.":
        "HFI \u542f\u52a8\u65f6\u4f7f\u7528\u7684\u7535\u538b\u3002",
    "The voltage used while running for HFI.":
        "HFI \u8fd0\u884c\u65f6\u4f7f\u7528\u7684\u7535\u538b\u3002",
    "The maximum voltage for HFI.":
        "HFI \u7684\u6700\u5927\u7535\u538b\u3002",
    "The gain for HFI.":
        "HFI \u7684\u589e\u76ca\u3002",
    "The maximum error for HFI position estimation.":
        "HFI \u4f4d\u7f6e\u4f30\u7b97\u7684\u6700\u5927\u8bef\u5dee\u3002",

    # ===== FOC Offsets =====
    "The mode for offset calibration.":
        "\u504f\u79fb\u6821\u51c6\u6a21\u5f0f\u3002",
    "The current offsets for the three phases.":
        "\u4e09\u76f8\u7535\u6d41\u504f\u79fb\u3002",
    "The voltage offsets for the three phases.":
        "\u4e09\u76f8\u7535\u538b\u504f\u79fb\u3002",

    # ===== Field Weakening =====
    "The maximum current for field weakening.":
        "\u5f31\u78c1\u6700\u5927\u7535\u6d41\u3002",
    "The duty cycle threshold where field weakening starts.":
        "\u5f31\u78c1\u5f00\u59cb\u7684\u5360\u7a7a\u6bd4\u9608\u503c\u3002",
    "The ramp time for field weakening current.":
        "\u5f31\u78c1\u7535\u6d41\u7684\u659c\u5761\u65f6\u95f4\u3002",
    "The Q current factor for field weakening.":
        "\u5f31\u78c1\u7684 Q \u7535\u6d41\u7cfb\u6570\u3002",

    # ===== FOC Speed / Overmodulation =====
    "The source for the speed measurement in FOC mode.":
        "FOC \u6a21\u5f0f\u4e0b\u901f\u5ea6\u6d4b\u91cf\u7684\u6765\u6e90\u3002",
    "The overmodulation factor for FOC.":
        "FOC \u7684\u8fc7\u8c03\u5236\u7cfb\u6570\u3002",
    "Use with caution as high values cause distortion.":
        "\u5c0f\u5fc3\u4f7f\u7528\uff0c\u9ad8\u503c\u4f1a\u5bfc\u81f4\u5931\u771f\u3002",

    # ===== PID Speed Controller =====
    "The proportional gain for the speed controller.":
        "\u901f\u5ea6\u63a7\u5236\u5668\u7684\u6bd4\u4f8b\u589e\u76ca\u3002",
    "The integral gain for the speed controller.":
        "\u901f\u5ea6\u63a7\u5236\u5668\u7684\u79ef\u5206\u589e\u76ca\u3002",
    "The derivative gain for the speed controller.":
        "\u901f\u5ea6\u63a7\u5236\u5668\u7684\u5fae\u5206\u589e\u76ca\u3002",
    "The minimum ERPM for the speed controller.":
        "\u901f\u5ea6\u63a7\u5236\u5668\u7684\u6700\u5c0f ERPM\u3002",
    "Allow braking in the speed controller.":
        "\u5141\u8bb8\u901f\u5ea6\u63a7\u5236\u5668\u4e2d\u7684\u5236\u52a8\u3002",
    "The maximum acceleration in ERPM per second.":
        "\u6bcf\u79d2\u6700\u5927\u52a0\u901f\u5ea6\uff08ERPM/s\uff09\u3002",

    # ===== PID Position Controller =====
    "The proportional gain for the position controller.":
        "\u4f4d\u7f6e\u63a7\u5236\u5668\u7684\u6bd4\u4f8b\u589e\u76ca\u3002",
    "The integral gain for the position controller.":
        "\u4f4d\u7f6e\u63a7\u5236\u5668\u7684\u79ef\u5206\u589e\u76ca\u3002",
    "The derivative gain for the position controller.":
        "\u4f4d\u7f6e\u63a7\u5236\u5668\u7684\u5fae\u5206\u589e\u76ca\u3002",

    # ===== Motor Setup =====
    "The number of motor poles.":
        "\u7535\u673a\u6781\u6570\u3002",
    "The gear ratio between the motor and the wheel.":
        "\u7535\u673a\u4e0e\u8f6e\u5b50\u4e4b\u95f4\u7684\u9f7f\u8f6e\u6bd4\u3002",
    "The diameter of the wheel in meters.":
        "\u8f6e\u5b50\u76f4\u5f84\uff08\u7c73\uff09\u3002",
    "The type of battery used.":
        "\u4f7f\u7528\u7684\u7535\u6c60\u7c7b\u578b\u3002",
    "The number of battery cells in series.":
        "\u7535\u6c60\u4e32\u8054\u7535\u82af\u6570\u3002",
    "The capacity of the battery in amp-hours.":
        "\u7535\u6c60\u5bb9\u91cf\uff08\u5b89\u65f6\uff09\u3002",
    "The no-load current of the motor.":
        "\u7535\u673a\u7684\u7a7a\u8f7d\u7535\u6d41\u3002",

    # ===== BMS =====
    "Type of BMS. This determines how BMS-related messages on the CAN-bus are interpreted.":
        "BMS \u7c7b\u578b\u3002\u51b3\u5b9a CAN \u603b\u7ebf\u4e0a BMS \u76f8\u5173\u6d88\u606f\u5982\u4f55\u89e3\u8bfb\u3002",
    "Choose how to limit the motor current based on data from the BMS.":
        "\u9009\u62e9\u5982\u4f55\u6839\u636e BMS \u6570\u636e\u9650\u5236\u7535\u673a\u7535\u6d41\u3002",

    # ===== BMS Temperature/SOC/VCell =====
    "The battery temperature above which battery current starts to get reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u6c60\u7535\u6d41\u7684\u7535\u6c60\u6e29\u5ea6\u3002",
    "The battery temperature above which battery current is not allowed and a fault is thrown.":
        "\u4e0d\u5141\u8bb8\u7535\u6c60\u7535\u6d41\u5e76\u89e6\u53d1\u6545\u969c\u7684\u7535\u6c60\u6e29\u5ea6\u3002",
    "The battery state of charge (SOC) below which battery current starts to get reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u6c60\u7535\u6d41\u7684\u7535\u6c60 SOC\u3002",
    "The battery state of charge (SOC) below which battery current is not allowed anymore.":
        "\u4e0d\u518d\u5141\u8bb8\u7535\u6c60\u7535\u6d41\u7684\u7535\u6c60 SOC\u3002",
    "The minimum cell voltage below which battery current starts to get reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u7535\u6c60\u7535\u6d41\u7684\u6700\u4f4e\u7535\u82af\u7535\u538b\u3002",
    "The minimum cell voltage below which battery current is not allowed anymore.":
        "\u4e0d\u518d\u5141\u8bb8\u7535\u6c60\u7535\u6d41\u7684\u6700\u4f4e\u7535\u82af\u7535\u538b\u3002",
    "The maximum cell voltage above which regen current starts to get reduced.":
        "\u5f00\u59cb\u964d\u4f4e\u56de\u751f\u7535\u6d41\u7684\u6700\u9ad8\u7535\u82af\u7535\u538b\u3002",
    "The maximum cell voltage above which regen current is not allowed anymore.":
        "\u4e0d\u518d\u5141\u8bb8\u56de\u751f\u7535\u6d41\u7684\u6700\u9ad8\u7535\u82af\u7535\u538b\u3002",

    # ===== BMS CAN Forward =====
    "Forward CAN-frames to local device as they are received.":
        "\u5c06\u6536\u5230\u7684 CAN \u5e27\u8f6c\u53d1\u5230\u672c\u5730\u8bbe\u5907\u3002",
    "This is useful when many BMSes are connected on a CAN-bus.":
        "\u5f53\u591a\u4e2a BMS \u8fde\u63a5\u5728 CAN \u603b\u7ebf\u4e0a\u65f6\u5f88\u6709\u7528\u3002",
    "Decrease the input and regen current as the battery gets too hot.":
        "\u7535\u6c60\u8fc7\u70ed\u65f6\u964d\u4f4e\u8f93\u5165\u548c\u56de\u751f\u7535\u6d41\u3002",
    "Decrease the input current as the state of charge (SOC) gets too low.":
        "SOC \u8fc7\u4f4e\u65f6\u964d\u4f4e\u8f93\u5165\u7535\u6d41\u3002",
    "Decrease the input current as the lowest cell voltage gets too low.":
        "\u6700\u4f4e\u7535\u82af\u7535\u538b\u8fc7\u4f4e\u65f6\u964d\u4f4e\u8f93\u5165\u7535\u6d41\u3002",
    "Decrease the input regen current as the highest cell voltage gets too high.":
        "\u6700\u9ad8\u7535\u82af\u7535\u538b\u8fc7\u9ad8\u65f6\u964d\u4f4e\u56de\u751f\u7535\u6d41\u3002",
    "If there is more than one BMS on the CAN-bus, the one with the highest value will be used.":
        "\u5982\u679c CAN \u603b\u7ebf\u4e0a\u6709\u591a\u4e2a BMS\uff0c\u5c06\u4f7f\u7528\u6700\u9ad8\u503c\u3002",
    "If there is more than one BMS on the CAN-bus, the one with the lowest value will be used.":
        "\u5982\u679c CAN \u603b\u7ebf\u4e0a\u6709\u591a\u4e2a BMS\uff0c\u5c06\u4f7f\u7528\u6700\u4f4e\u503c\u3002",

    # ===== Faults =====
    "The fault stop time in milliseconds.":
        "\u6545\u969c\u505c\u6b62\u65f6\u95f4\uff08\u6beb\u79d2\uff09\u3002",
    "Additional fault settings for the motor.":
        "\u7535\u673a\u7684\u9644\u52a0\u6545\u969c\u8bbe\u7f6e\u3002",

    # ===== App Selection =====
    "Select which app to use for controlling the VESC.":
        "\u9009\u62e9\u7528\u4e8e\u63a7\u5236 VESC \u7684\u5e94\u7528\u7a0b\u5e8f\u3002",

    # ===== PPM / ADC / NRF / Nunchuk / PAS / UART / IMU Config =====
    "Configure the PPM input mapping.":
        "\u914d\u7f6e PPM \u8f93\u5165\u6620\u5c04\u3002",
    "Configure the ADC input mapping.":
        "\u914d\u7f6e ADC \u8f93\u5165\u6620\u5c04\u3002",
    "Configure the NRF controller.":
        "\u914d\u7f6e NRF \u63a7\u5236\u5668\u3002",
    "Configure the Nunchuk controller.":
        "\u914d\u7f6e Nunchuk \u63a7\u5236\u5668\u3002",
    "Configure the PAS (Pedal Assist System).":
        "\u914d\u7f6e PAS\uff08\u8e0f\u677f\u8f85\u52a9\u7cfb\u7edf\uff09\u3002",
    "Configure the UART app.":
        "\u914d\u7f6e UART \u5e94\u7528\u3002",
    "Configure the IMU settings.":
        "\u914d\u7f6e IMU \u8bbe\u7f6e\u3002",
}


def process_file(filepath):
    """Translate description elements in a single XML file. Returns count of translations."""
    if not os.path.exists(filepath):
        return 0

    tree = ET.parse(filepath)
    root = tree.getroot()
    count = 0

    for elem in root.iter():
        tag = elem.tag.lower() if "}" not in elem.tag else elem.tag.split("}", 1)[1]

        if tag == "description" and elem.text:
            original = elem.text
            modified = original

            for en_text, cn_text in DESCRIPTION_PATTERNS.items():
                if en_text in modified:
                    modified = modified.replace(en_text, cn_text)
                    count += 1

            if modified != original:
                elem.text = modified

    if count > 0:
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    return count


def main():
    if not os.path.isdir(BASE):
        print(f"ERROR: Directory not found: {BASE}")
        sys.exit(1)

    versions = sorted([
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d))
    ])

    total_descriptions = 0
    files_modified = 0

    for ver in versions:
        mcc = os.path.join(BASE, ver, "parameters_mcconf.xml")
        apc = os.path.join(BASE, ver, "parameters_appconf.xml")

        for fp in (mcc, apc):
            n = process_file(fp)
            if n > 0:
                total_descriptions += n
                files_modified += 1
                rel = os.path.relpath(fp, os.path.dirname(BASE))
                print(f"  {rel}: {n} description replacements")

    print()
    print(f"=== Summary ===")
    print(f"   Description replacements: {total_descriptions}")
    print(f"   Files modified:          {files_modified}")
    print(f"   Versions processed:      {len(versions)}")

    print()
    print("Verifying output...")
    verify = os.path.join(BASE, "7.00", "parameters_mcconf.xml")
    try:
        ET.parse(verify)
        print(f"  {os.path.relpath(verify)}: OK")
    except ET.ParseError as e:
        print(f"  {os.path.relpath(verify)}: BROKEN - {e}")

    verify = os.path.join(BASE, "7.00", "parameters_appconf.xml")
    try:
        ET.parse(verify)
        print(f"  {os.path.relpath(verify)}: OK")
    except ET.ParseError as e:
        print(f"  {os.path.relpath(verify)}: BROKEN - {e}")


if __name__ == "__main__":
    main()
