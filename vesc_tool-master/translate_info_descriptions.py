#!/usr/bin/env python3
"""
Translate info.xml description blocks from English to Chinese across all VESC firmware versions.
Uses pattern-based substring replacement, preserving all HTML formatting.
"""

import os
import re
import glob
import html
import xml.etree.ElementTree as ET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_ROOT = os.path.join(SCRIPT_DIR, "res", "config")


# ---------------------------------------------------------------------------
# Translation pairs: (english_text, chinese_text)
# These operate on the raw HTML string stored in the <description> element.
# Order matters: longer / more specific patterns MUST come before shorter ones.
# All translations use exact substring matching.
# ---------------------------------------------------------------------------
TRANSLATIONS = [
    # ========================================================================
    # motor_setting_description
    # ========================================================================

    # Title
    (">Motor Settings<", ">电机设置<"),

    # Paragraph 1 — text split by <span> tag around "very important" and "Motor Setup Wizard"
    # Original: This is where you can edit your motor settings. It is <span...>very important</span>
    #           to setup your VESC every time you connect a different motor, otherwise the VESC
    #           and/or the motor are likely to get damaged. The easiest way to set up your VESC
    #           for your motor is to use the <span...>Motor Setup Wizard</span>. This wizard can
    #           be accessed from the welcome page, from the help menu or using the button at
    #           the bottom of this page.
    (
        "This is where you can edit your motor settings. It is ",
        "您可以在此处编辑电机设置。",
    ),
    # "very important" appears inside a color span; handle both font variants
    (">very important</span>", ">非常重要</span>"),
    (
        " to setup your VESC every time you connect a different motor, "
        "otherwise the VESC and/or the motor are likely to get damaged. "
        "The easiest way to set up your VESC for your motor is to use the ",
        "每次连接不同的电机时，重新设置 VESC 非常重要，否则 VESC 和/或电机可能会损坏。"
        "为电机设置 VESC 最简单的方法是使用",
    ),
    (">Motor Setup Wizard<", ">电机设置向导<"),
    (
        ". This wizard can be accessed from the welcome page, "
        "from the help menu or using the button at the bottom of this page.",
        "。此向导可以从欢迎页面、帮助菜单或使用本页底部的按钮访问。",
    ),

    # Paragraph 2
    (
        "The motor settings are stored in their own configuration structure. "
        "Every time you make changes to the motor configuration you have to write "
        "the configuration to the VESC in order to apply the new settings. "
        "Reading/writing the motor configuration can be done using the buttons "
        "on the toolbar to the right. "
        "The functions of these toolbar buttons are the following:",
        "电机设置存储在其自身的配置结构中。"
        "每次更改电机配置后，您必须将配置写入 VESC 才能应用新设置。"
        "可以使用右侧工具栏上的按钮读取/写入电机配置。"
        "这些工具栏按钮的功能如下：",
    ),

    # Toolbar buttons — name in <span>, followed by text
    (">Read Motor Configuration<", ">读取电机配置<"),
    (
        ". This button will read the current motor configuration from the VESC to VESC Tool.",
        "。此按钮将从 VESC 读取当前电机配置到 VESC Tool。",
    ),

    # Warning: "Warning" is inside a color span: <span...>Warning</span>: text...
    (
        '>Warning</span>: All of the motor settings currently in VESC Tool will be overwritten by pressing this button.',
        '>警告</span>：按下此按钮将覆盖 VESC Tool 中当前的所有电机设置。',
    ),

    (">Read Default Motor Configuration<", ">读取默认电机配置<"),
    (
        ". This button will read the default motor configuration from the VESC to VESC Tool. "
        "The default configuration is hard-coded in firmware, and is how the VESC is configured "
        "right after uploading new firmware.",
        "。此按钮将从 VESC 读取默认电机配置到 VESC Tool。"
        "默认配置在固件中硬编码，是上传新固件后 VESC 的配置状态。",
    ),

    (">Write Motor Configuration<", ">写入电机配置<"),
    (
        ". This button will write the motor configuration that currently is in VESC Tool to the VESC. "
        "Every time you make a change to the motor configuration in VESC Tool "
        "you must use this button to apply the new settings. "
        "The new settings will be used as soon as you write them to the VESC, "
        "and they will be stored in the flash memory of the VESC persistently.",
        "。此按钮将 VESC Tool 中当前的电机配置写入 VESC。"
        "在 VESC Tool 中每次更改电机配置后，必须使用此按钮来应用新设置。"
        "新设置将在写入 VESC 后立即生效，并持久存储在 VESC 的闪存中。",
    ),

    # Per-setting buttons
    (
        "Every motor setting has three small buttons to the right of its value. "
        "They have the following functions:",
        "每个电机设置在其值右侧有三个小按钮。它们的功能如下：",
    ),

    (">Read Current Value<", ">读取当前值<"),
    (
        ". This button will read the current value for this setting from the VESC.",
        "。此按钮将从 VESC 读取此设置的当前值。",
    ),

    (">Read Default Value<", ">读取默认值<"),
    (
        ". This button will read the default value for this setting from the VESC.",
        "。此按钮将从 VESC 读取此设置的默认值。",
    ),

    (">Show Help<", ">显示帮助<"),
    (
        ". This button will show a help dialog describing what this setting does. "
        "If you are not sure about a setting the help dialog can be very useful.",
        "。此按钮将显示一个帮助对话框，描述此设置的作用。"
        "如果不确定某个设置，帮助对话框会非常有用。",
    ),

    # File menu paragraph — long form (with both sentences)
    (
        'The full motor configuration, including the notes you make on the '
        '<span style=" font-weight:600;">Description</span> page, can also be written to and read from XML files using the '
        '<span style=" font-weight:600;">File</span> menu. '
        "This is a good way to keep your settings when going between different VESC Tool versions, "
        "to share your settings and to store your configuration in general.",
        '完整的电机配置（包括您在'
        '<span style=" font-weight:600;">描述</span>页面上所做的笔记）也可以使用'
        '<span style=" font-weight:600;">文件</span>菜单写入和读取 XML 文件。'
        "这是在不同 VESC Tool 版本之间保留设置、分享设置以及存储配置的好方法。",
    ),
    # Short form (just the first sentence)
    (
        'The full motor configuration, including the notes you make on the '
        '<span style=" font-weight:600;">Description</span> page, can also be written to and read from XML files using the '
        '<span style=" font-weight:600;">File</span> menu.',
        '完整的电机配置（包括您在'
        '<span style=" font-weight:600;">描述</span>页面上所做的笔记）也可以使用'
        '<span style=" font-weight:600;">文件</span>菜单写入和读取 XML 文件。',
    ),
    # Older versions: font-family:'Roboto' variant — long form
    (
        "The full motor configuration, including the notes you make on the "
        '>Description< page, can also be written to and read from XML files using the '
        '>File< menu. '
        "This is a good way to keep your settings when going between different VESC Tool versions, "
        "to share your settings and to store your configuration in general.",
        "完整的电机配置（包括您在"
        ">描述<页面上所做的笔记）也可以使用"
        ">文件<菜单写入和读取 XML 文件。"
        "这是在不同 VESC Tool 版本之间保留设置、分享设置以及存储配置的好方法。",
    ),
    # Older versions: font-family:'Roboto' variant — short form
    (
        "The full motor configuration, including the notes you make on the "
        '>Description< page, can also be written to and read from XML files using the '
        '>File< menu.',
        "完整的电机配置（包括您在"
        ">描述<页面上所做的笔记）也可以使用"
        ">文件<菜单写入和读取 XML 文件。",
    ),
    # Generic sentence for "good way to keep..."
    (
        "This is a good way to keep your settings when going between different VESC Tool versions, "
        "to share your settings and to store your configuration in general.",
        "这是在不同 VESC Tool 版本之间保留设置、分享设置以及存储配置的好方法。",
    ),

    # Notice about firmware uploading
    (
        "Notice that uploading new firmware to the VESC will reset all its settings "
        "to their default values for that firmware. "
        "This means that after uploading firmware to the VESC you have to perform "
        "the motor configuration again.",
        "请注意，向 VESC 上传新固件会将其所有设置重置为该固件的默认值。"
        "这意味着在向 VESC 上传固件后，您必须重新进行电机配置。",
    ),

    # ========================================================================
    # app_setting_description
    # ========================================================================

    (">App Settings<", ">应用设置<"),

    (
        "This is where you can edit your app settings. "
        "The VESC can run one or more apps, and the apps are used to enable "
        "different functions on the communication interfaces of the VESC. "
        "If you are going to use your VESC with USB or CAN-bus you don't "
        "have to change the app configuration since these interfaces always are active. "
        "If you want to use conventional input devices such as nunchuks, "
        "ebike throttles or RC remote controllers you have to configure the apps accordingly.",
        "您可以在此处编辑应用设置。"
        "VESC 可以运行一个或多个应用，这些应用用于启用 VESC 通信接口上的不同功能。"
        "如果您通过 USB 或 CAN 总线使用 VESC，则无需更改应用配置，因为这些接口始终处于活动状态。"
        "如果要使用传统输入设备（如 nunchuk、电动车油门或 RC 遥控器），则必须相应配置应用。",
    ),
    # app_setting_description: "easiest way" intro paragraph (text before the span)
    (
        "The easiest way to configure your VESC for conventional input devices is to use the ",
        "为 VESC 配置传统输入设备最简单的方法是使用",
    ),
    # The ">Input Setup Wizard<" -> ">输入设置向导<" is handled by TAG_SAFE_REPLACEMENTS.
    # But the exact pattern in TRANSLATIONS needs to match the text WITH the span.
    # Since span tags vary, we handle the post-span text here:
    (
        ">Input Setup Wizard</span>. "
        "This wizard can be accessed from the welcome page, "
        "from the help menu or using the button at the bottom of this page.",
        ">输入设置向导</span>。"
        "此向导可以从欢迎页面、帮助菜单或使用本页底部的按钮访问。",
    ),

    (
        "The app settings are stored in their own configuration structure. "
        "Every time you make changes to the app configuration you have to write "
        "the configuration to the VESC in order to apply the new settings. "
        "Reading/writing the app configuration can be done using the buttons "
        "on the toolbar to the right. "
        "The functions of these toolbar buttons are the following:",
        "应用设置存储在其自身的配置结构中。"
        "每次更改应用配置后，您必须将配置写入 VESC 才能应用新设置。"
        "可以使用右侧工具栏上的按钮读取/写入应用配置。"
        "这些工具栏按钮的功能如下：",
    ),

    (">Read App Configuration<", ">读取应用配置<"),
    (
        ". This button will read the current app configuration from the VESC to VESC Tool.",
        "。此按钮将从 VESC 读取当前应用配置到 VESC Tool。",
    ),
    (
        '>Warning</span>: All of the app settings currently in VESC Tool will be overwritten by pressing this button.',
        '>警告</span>：按下此按钮将覆盖 VESC Tool 中当前的所有应用设置。',
    ),

    (">Read Default App Configuration<", ">读取默认应用配置<"),
    (
        ". This button will read the default app configuration from the VESC to VESC Tool. "
        "The default configuration is hard-coded in firmware, and is how the VESC is configured "
        "right after uploading new firmware.",
        "。此按钮将从 VESC 读取默认应用配置到 VESC Tool。"
        "默认配置在固件中硬编码，是上传新固件后 VESC 的配置状态。",
    ),

    (">Write App Configuration<", ">写入应用配置<"),
    (
        ". This button will write the app configuration that currently is in VESC Tool to the VESC. "
        "Every time you make a change to the app configuration in VESC Tool "
        "you must use this button to apply the new settings. "
        "The new settings will be used as soon as you write them to the VESC, "
        "and they will be stored in the flash memory of the VESC persistently.",
        "。此按钮将 VESC Tool 中当前的应用配置写入 VESC。"
        "在 VESC Tool 中每次更改应用配置后，必须使用此按钮来应用新设置。"
        "新设置将在写入 VESC 后立即生效，并持久存储在 VESC 的闪存中。",
    ),

    (
        "Every app setting has three small buttons to the right of its value. "
        "They have the following functions:",
        "每个应用设置在其值右侧有三个小按钮。它们的功能如下：",
    ),

    # File menu paragraph — long form (with both sentences)
    (
        'The full app configuration can also be written to and read from XML files using the '
        '<span style=" font-weight:600;">File</span> menu. '
        "This is a good way to keep your settings when going between different VESC Tool versions, "
        "to share your settings and to store your configuration in general.",
        '完整的应用配置也可以使用'
        '<span style=" font-weight:600;">文件</span>菜单写入和读取 XML 文件。'
        "这是在不同 VESC Tool 版本之间保留设置、分享设置以及存储配置的好方法。",
    ),
    # Short form
    (
        'The full app configuration can also be written to and read from XML files using the '
        '<span style=" font-weight:600;">File</span> menu.',
        '完整的应用配置也可以使用'
        '<span style=" font-weight:600;">文件</span>菜单写入和读取 XML 文件。',
    ),
    # Older versions with font-family:'Roboto' — long
    (
        "The full app configuration can also be written to and read from XML files using the "
        '>File< menu. '
        "This is a good way to keep your settings when going between different VESC Tool versions, "
        "to share your settings and to store your configuration in general.",
        "完整的应用配置也可以使用"
        ">文件<菜单写入和读取 XML 文件。"
        "这是在不同 VESC Tool 版本之间保留设置、分享设置以及存储配置的好方法。",
    ),
    # Older versions — short
    (
        "The full app configuration can also be written to and read from XML files using the "
        '>File< menu.',
        "完整的应用配置也可以使用"
        ">文件<菜单写入和读取 XML 文件。",
    ),

    (
        "Notice that uploading new firmware to the VESC will reset all its settings "
        "to their default values for that firmware. "
        "This means that after uploading firmware to the VESC you have to perform "
        "the app configuration again.",
        "请注意，向 VESC 上传新固件会将其所有设置重置为该固件的默认值。"
        "这意味着在向 VESC 上传固件后，您必须重新进行应用配置。",
    ),

    # ========================================================================
    # wizard_startup_intro (Welcome page)
    # ========================================================================

    (
        "Welcome to ",
        "欢迎使用 ",
    ),
    (
        ". Since this is the first time you start this version of VESC Tool, "
        "the introduction is shown. "
        "Please read all instructions carefully for your own safety.",
        "。由于这是您首次启动此版本的 VESC Tool，因此会显示介绍。"
        "为了您的安全，请仔细阅读所有说明。",
    ),

    # ========================================================================
    # dev_tools_description
    # ========================================================================

    (">VESC Development Tools<", ">VESC 开发工具<"),

    (
        "This is a text command interface to some advanced and debug-functions of the hardware.",
        "这是一个针对硬件高级和调试功能的文本命令界面。",
    ),

    (
        "Qml is an extension of javascript that is used to make mobile applications in Qt. "
        "The mobile version of VESC Tool as well as the wizards in the desktop version "
        "are written in Qml. The Qml-editor in VESC Tool can be used to write custom "
        "user interface pages that are loaded and run in VESC Tool. "
        "There are many examples available that can be used as a starting point.",
        "QML 是 JavaScript 的扩展，用于在 Qt 中制作移动应用程序。"
        "移动版 VESC Tool 以及桌面版的向导都是用 QML 编写的。"
        "VESC Tool 中的 QML 编辑器可用于编写自定义用户界面页面，这些页面可在 VESC Tool 中加载和运行。"
        "有许多可用作起点的示例。",
    ),

    (
        "The VESC motor control firmware as well as the VESC Express firmware "
        "have a built-in version of LispBM, which is a modern embedded scripting "
        "language based on lisp. Code written in LispBM runs directly on the hardware "
        "and can be used for custom functionality not covered by the basic applications.",
        "VESC 电机控制固件以及 VESC Express 固件都内置了 LispBM，这是一种基于 Lisp 的现代嵌入式脚本语言。"
        "用 LispBM 编写的代码直接在硬件上运行，可用于基本应用未涵盖的自定义功能。",
    ),

    (
        "Simple CAN-bus tool that can read and send messages on the CAN-bus.",
        "简单的 CAN 总线工具，可以在 CAN 总线上读取和发送消息。",
    ),

    (
        "Graphic and font generation tool for displays supported by the VESC display driver, "
        "which is part of the Express firmware.",
        "用于 VESC 显示驱动程序支持的显示器的图形和字体生成工具，该驱动程序是 Express 固件的一部分。",
    ),

    (
        "Debug messages from VESC Tool are printed here.",
        "VESC Tool 的调试消息在此处打印。",
    ),

    # ========================================================================
    # data_analysis_description
    # ========================================================================

    (">Data Analysis<", ">数据分析<"),

    (
        "Here you can stream and plot data from the VESC to analyze what is going on. "
        "Next to all plots the following buttons are available:",
        "您可以在此处从 VESC 流式传输和绘制数据，以分析正在发生的情况。"
        "所有图表旁边都有以下按钮：",
    ),

    (
        "If this button is toggled active (blue), scolling with the mouse "
        "on the graph will zoom the graph horizontally.",
        "如果此按钮切换为激活状态（蓝色），在图表上滚动鼠标滚轮将水平缩放图表。",
    ),

    (
        "If this button is toggled active (blue), scolling with the mouse "
        "on the graph will zoom the graph vertically. "
        "Often it is useful to deactivate this button and only zoom in the "
        "horizontal direction because the sampled data can be squeezed "
        "together horizontally for long sampling sequences.",
        "如果此按钮切换为激活状态（蓝色），在图表上滚动鼠标滚轮将垂直缩放图表。"
        "通常，停用此按钮并仅在水平方向缩放是有用的，"
        "因为长时间的采样序列可能会使采样数据在水平方向上被挤压。",
    ),

    (
        "This is the auto fit button. "
        "If the toggle verion of the button is active (blue), "
        "new realtime data that drops in will cause a rezoom in the graph to fit all data. "
        "Deactivating this button can be useful of you want to zoom in on "
        "the realtime data manually while samples are dropping in.",
        "这是自动适应按钮。"
        "如果此按钮的切换版本处于激活状态（蓝色），"
        "新的实时数据到来时将重新缩放图表以适应所有数据。"
        "如果您想在样本到达时手动放大实时数据，停用此按钮可能会很有用。",
    ),

    (
        "This is the non-toggle version of the auto fit button. "
        "Pressing it will zoom the plots so that all data fits in them.",
        "这是自动适应按钮的非切换版本。"
        "按下它会缩放图表，使所有数据都适应其中。",
    ),

    (">Realtime Data<", ">实时数据<"),
    (
        "The realtime data page can be used to stream and plot filtered data continuously, "
        "which can be useful for visualizing things in real time while they are happening. "
        "For example, if you run a motor and put some load on it, "
        "you can see that reflected right away in the current and RPM graphs. "
        "Tuning the position and speed PID control parameters is also a lot easier "
        "when looking at the step response in a graph.",
        "实时数据页面可用于连续流式传输和绘制过滤后的数据，"
        "这对于在事情发生时实时可视化非常有用。"
        "例如，如果运行电机并对其施加负载，可以立即在电流和 RPM 图表中看到反映。"
        "在查看图表中的阶跃响应时，调整位置和速度 PID 控制参数也会容易得多。",
    ),

    (
        "In ordet to stream realtime data, the "
        '>Stream realtime data< button in the main toolbar to the right has to be activated:',
        "要流式传输实时数据，必须激活右侧主工具栏中的"
        ">流式传输实时数据<按钮：",
    ),

    (">Sampled Data<", ">采样数据<"),
    (
        "The sampled data page can be used to sample data at high rate internally "
        "on the VESC and send it back for plotting after that. "
        "This page can be used to visualize all samples taken by the ADCs "
        "to analyze the current and voltage waveforms in detail. "
        "Since this data is sampled at such a high rate it cannot be "
        "streamed in real time, which is why sampling and plotting has to be toggled manually. "
        "There are two buttons for starting the sampling in the lower toolbar in this page:",
        "采样数据页面可用于在 VESC 内部以高速率采样数据，然后将其发回进行绘图。"
        "此页面可用于可视化 ADC 采集的所有样本，以详细分析电流和电压波形。"
        "由于这些数据以如此高的速率采样，无法实时流式传输，因此必须手动切换采样和绘图。"
        "此页面下方的工具栏中有两个用于启动采样的按钮：",
    ),

    (
        "Sample data now and send it when this is done.",
        "立即采样数据并在完成后发送。",
    ),

    (
        "Sample data the next time the motor starts moving. "
        "This can be useful to analyze the startup behaviour in real time.",
        "在电机下次开始移动时采样数据。"
        "这对于实时分析启动行为非常有用。",
    ),

    (
        "There are also options to apply filters to the sampled data "
        "and/or to plot a FFT of all samples if desired.",
        "还有选项可以对采样数据应用滤波器和/或根据需要绘制所有样本的 FFT。",
    ),

    # ========================================================================
    # help_battery_cutoff
    # ========================================================================

    (
        "Parameters for a soft battery cutoff can be calculated here. "
        "To do that, select the battery type and amount of cells. "
        "When the battery voltage is at the start value, the battery current "
        "will start to get reduced. At the end value battery current draw "
        "(and thus motor current) is disabled completely. "
        "In between the current is limited proportionally to where between "
        "the start and end values the input voltage is.",
        "可以在此计算软电池截止参数。"
        "为此，请选择电池类型和电池数量。"
        "当电池电压处于起始值时，电池电流将开始减小。"
        "在截止值时，电池电流（以及因此的电机电流）将完全禁用。"
        "在两者之间，电流根据输入电压在起始值和截止值之间的位置按比例限制。",
    ),

    (
        "Notice that braking always is possible, even when the battery current is limited. "
        "That is because braking does not draw any current from the battery, "
        "it only charges the battery.",
        "请注意，即使电池电流受限，制动仍然可能。"
        "这是因为制动不会从电池汲取电流，只会给电池充电。",
    ),

    # ========================================================================
    # help_bldc_detect
    # ========================================================================

    (
        "Spin up the motor in delay commutation mode and try to measure "
        "the following parameters:",
        "在延迟换向模式下启动电机，并尝试测量以下参数：",
    ),
    (">Cycle Integrator Limit<", ">周期积分器限制<"),
    (">BEMF Coupling<", ">反电动势耦合<"),
    (">Hall Sensor Table<", ">霍尔传感器表<"),

    (
        "The settings mean the following:",
        "这些设置的含义如下：",
    ),

    (">Current (I)<", ">电流 (I)<"),
    (
        "The current to use for spinning up the motor.",
        "用于启动电机的电流。",
    ),

    (">ERPM (ω)<", ">ERPM (ω)<"),
    (
        "The minimum speed for the delay commutation mode to start the motor.",
        "延迟换向模式启动电机的最低速度。",
    ),

    (">Duty (D)<", ">占空比 (D)<"),
    (
        "The duty cycle to measure the BEMF coupling at. "
        "This value should be as low as possible, but not so low that the motor "
        "cannot spin at the end of the detection sequence.",
        "测量反电动势耦合的占空比。"
        "此值应尽可能低，但不要太低，以免电机在检测序列结束时无法旋转。",
    ),

    (
        "If the motor is not able to spin up properly these settings can be tweaked. Symptoms:",
        "如果电机无法正常启动，可以调整这些设置。症状：",
    ),

    (
        "The motor starts to spin, but is too weak to reach enough speed.",
        "电机开始旋转，但太弱无法达到足够的转速。",
    ),
    (
        "Increase the current setting.",
        "增加电流设置。",
    ),

    (
        "The motor cogs and is unable to spin up.",
        "电机卡顿，无法启动。",
    ),
    (
        "Increase or decrease the current.",
        "增加或减少电流。",
    ),
    (
        "If the motor has high inertia decrease ERPM. "
        "E-bike hub motors tend to have high inertia.",
        "如果电机惯量大，请降低 ERPM。电动车轮毂电机往往具有较大的惯量。",
    ),
    (
        "If the motor has low inertia increase ERPM.",
        "如果电机惯量小，请增加 ERPM。",
    ),

    (
        "The motor spins up properly, but does not spin at the end of the detection.",
        "电机正常启动，但在检测结束时不会旋转。",
    ),
    (
        "Increase the duty and try again. "
        "This is usually needed for low KV motor when using low voltage, "
        "such as ebike motors.",
        "增加占空比并重试。"
        "当使用低电压时，低 KV 电机（如电动车电机）通常需要这样做。",
    ),

    # ========================================================================
    # help_foc_detect
    # ========================================================================

    (
        "Detect and calculate the necessary FOC motor and control parameters. "
        "The procedure is the following:",
        "检测并计算必要的 FOC 电机和控制参数。步骤如下：",
    ),

    (
        "Measure <span style=\" font-weight:600;\">R</span> and <span style=\" font-weight:600;\">L</span>"
        " and wait for the detection result. "
        "When the detection result arrives, "
        "<span style=\" font-weight:600;\">KP</span>, "
        "<span style=\" font-weight:600;\">KI</span> and "
        "<span style=\" font-weight:600;\">Observer Gain</span> will be calculated.",
        "测量 <span style=\" font-weight:600;\">R</span> 和 <span style=\" font-weight:600;\">L</span>"
        " 并等待检测结果。当检测结果到达时，"
        "<span style=\" font-weight:600;\">KP</span>、"
        "<span style=\" font-weight:600;\">KI</span> 和 "
        "<span style=\" font-weight:600;\">观测器增益</span>将被计算。",
    ),

    (
        "Measure <span style=\" font-weight:600;\">λ</span>"
        " and wait for the detection result. If the detections fails, tweak "
        "<span style=\" font-weight:600;\">I</span>, "
        "<span style=\" font-weight:600;\">D</span> and "
        "<span style=\" font-weight:600;\">ω </span>as described below and try again until it works.",
        "测量 <span style=\" font-weight:600;\">λ</span>"
        " 并等待检测结果。如果检测失败，请调整 "
        "<span style=\" font-weight:600;\">I</span>、"
        "<span style=\" font-weight:600;\">D</span> 和 "
        "<span style=\" font-weight:600;\">ω </span>如下所述，然后重试直到成功。",
    ),

    (
        "Use the <span style=\" font-weight:600;\">Apply</span> button to apply the measured and calculated parameters.",
        "使用 <span style=\" font-weight:600;\">应用</span>按钮来应用测量和计算的参数。",
    ),

    (
        "The following parameters are measured:",
        "以下参数被测量：",
    ),

    (">Resistance (R)<", ">电阻 (R)<"),
    (">Inductance (L)<", ">电感 (L)<"),
    (">Flux Linkage (λ)<", ">磁链 (λ)<"),

    (
        "The following parameter are calculated from "
        "<span style=\" font-weight:600;\">R</span> and "
        "<span style=\" font-weight:600;\">L</span>:",
        "以下参数由 "
        "<span style=\" font-weight:600;\">R</span> 和 "
        "<span style=\" font-weight:600;\">L</span> 计算得出：",
    ),

    (">Proportional gain for the current controller (KP)<", ">电流控制器的比例增益 (KP)<"),
    (">Integral gain for the current controller (KI)<", ">电流控制器的积分增益 (KI)<"),
    (">Gain for the observer<", ">观测器增益<"),

    (
        "For measuring resistance and inductance, signals are injected into the motor. "
        "Nothing requires configuration for doing that and the motor does not need to spin up.",
        "为了测量电阻和电感，信号被注入电机中。"
        "无需进行任何配置，电机也不需要启动。",
    ),

    (
        "For measuring the flux linkage the motor needs to spin up, "
        "which is controlled by the "
        "<span style=\" font-weight:600;\">I</span>, "
        "<span style=\" font-weight:600;\">D</span> and "
        "<span style=\" font-weight:600;\">ω</span> startup settings. "
        "Notice that the resistance has to be measured first. "
        "The startup settings mean the following:",
        "为了测量磁链，电机需要启动，这由"
        "<span style=\" font-weight:600;\">I</span>、"
        "<span style=\" font-weight:600;\">D</span> 和 "
        "<span style=\" font-weight:600;\">ω</span> 启动设置控制。"
        "请注意，必须先测量电阻。启动设置的含义如下：",
    ),

    (
        "The duty cycle where to measure the flux linkage.",
        "测量磁链的占空比。",
    ),

    (
        "If the load increases with speed (e.g. a propeller) "
        "you can decrease the duty cycle. "
        "This makes the detection slightly less accurate, "
        "but that does not matter in general.",
        "如果负载随速度增加（例如螺旋桨），可以降低占空比。"
        "这会使检测精度稍低，但通常无关紧要。",
    ),

    (
        "After measuring the motor parameters, gain factors for the current PI control loop "
        "and the observer gain should be calculated. "
        "KP and KI are calculated based on a desired time constant of the current controller "
        "and the motor parameters R and L, which have to be measured first. "
        "The observer gain is calculated based on the motor inductance, "
        "which also has to be measured first.",
        "测量电机参数后，应计算电流 PI 控制回路的增益因子和观测器增益。"
        "KP 和 KI 根据电流控制器的期望时间常数以及电机参数 R 和 L 计算，这些参数必须首先测量。"
        "观测器增益根据电机电感计算，这也必须首先测量。",
    ),

    # ========================================================================
    # help_foc_encoder_detect
    # ========================================================================

    (
        "Detect the following encoder parameters:",
        "检测以下编码器参数：",
    ),
    (">Offset<", ">偏移<"),
    (">Ratio<", ">比率<"),
    (">Inverted<", ">反转<"),

    (
        "To do that, the motor is turned slowly in open loop while the encoder output is sampled, "
        "once for the ratio and once for the offset. "
        "This is done in both directions for one full mechanical revolution "
        "to get rid off possible offsets and nonlinearities.",
        "为此，电机在开环中缓慢旋转，同时采样编码器输出，一次用于比率，一次用于偏移。"
        "此操作在两个方向上各进行一次完整的机械旋转，以消除可能的偏移和非线性。",
    ),

    # ========================================================================
    # help_foc_hall_detect
    # ========================================================================

    (
        "Detect the hall sensor table. "
        "To do that, the motor is turned slowly in open loop while the hall sensor outputs are sampled. "
        "This is done in both directions to get rid of offsets.",
        "检测霍尔传感器表。"
        "为此，电机在开环中缓慢旋转，同时采样霍尔传感器输出。"
        "此操作在两个方向上各进行一次，以消除偏移。",
    ),

    # ========================================================================
    # help_nrf_pair
    # ========================================================================

    (
        "Set the VESC in NRF pairing mode for the amount of time specified in the Time box "
        "(default 10 seconds). Afer that, you should put the device to pair in pairing mode "
        "before the time runs out. A popup should appear and show that pairing was successful, "
        "or that it timed out. After a sucessful pairing, the NRF settings will be updated "
        "according to the unique ID of the paired NRF device and stored to the VESC.",
        "将 VESC 设置为 NRF 配对模式，配对时间由时间框中的值指定（默认 10 秒）。"
        "之后，您应在超时前将待配对设备设置为配对模式。"
        "将弹出一个弹窗，显示配对成功或超时。"
        "成功配对后，NRF 设置将根据配对 NRF 设备的唯一 ID 进行更新并存储到 VESC。",
    ),

    # keep NRF Nunchuk as-is
    (
        "For pairing the NRF nunchuk, set the VESC in pairing mode and switch on a nunchuk "
        "(that was switched off previously) before the pairing time runs out.",
        "要配对 NRF nunchuk，请将 VESC 设置为配对模式，并在配对超时前打开 nunchuk（之前已关闭）。",
    ),

    (
        "Notice that the unique ID of the NRF nunchuk is based on a hashed version "
        "of its microcontroller UUID, so the pairing should still be valid even after "
        "updating firmware. The chance of collisions between NRF nunchuks is practically non-existent.",
        "请注意，NRF nunchuk 的唯一 ID 基于其微控制器 UUID 的哈希版本，因此即使在更新固件后，"
        "配对也应仍然有效。NRF nunchuk 之间的冲突几率实际上不存在。",
    ),

    # ========================================================================
    # help_can_forward
    # ========================================================================

    (
        "When CAN forwarding is enabled, all communication will be forwarded over CAN bus "
        "to the VESC with the ID selected in the ID box in the connection page.",
        "启用 CAN 转发后，所有通信将通过 CAN 总线转发到连接页面 ID 框中选定的 ID 对应的 VESC。",
    ),

    # ========================================================================
    # help_rt_logging
    # ========================================================================

    (
        "VESC Tool (mobile and desktop) can log realtime data to CSV files. "
        "The output directory has to be chosen, which is where the log files are stored. "
        "Each time the logging checkbox is checked, a new CSV file with the current date "
        "and time is created in the output directory. "
        "This means that toggling the box will store the current file create a new one, "
        "which can be convenient to split the logs.",
        "VESC Tool（移动版和桌面版）可以将实时数据记录到 CSV 文件中。"
        "必须选择输出目录，日志文件将存储在其中。"
        "每次勾选日志复选框时，都会在输出目录中创建一个带有当前日期和时间的新 CSV 文件。"
        "这意味着切换该框将存储当前文件并创建一个新文件，这可以方便地分割日志。",
    ),

    (
        "The output format is as follows:",
        "输出格式如下：",
    ),

    (
        "The values mean the following:",
        "这些值的含义如下：",
    ),

    (
        "Time today in milliseconds. "
        "This time is sampled in VESC Tool, so it can contain jitter compared to the data values "
        "depending in transmission latency.",
        "今日时间，以毫秒为单位。"
        "此时间在 VESC Tool 中采样，因此根据传输延迟，与数据值相比可能包含抖动。",
    ),

    (
        "MOSFET temperature in ",
        "MOSFET 温度，单位为",
    ),
    (
        "°C.",
        "°C。",
    ),

    (
        "Individual MOSFET temperatures for the legs in the power stage in ",
        "功率级中各个支路 MOSFET 的温度，单位为",
    ),
    (
        "°C. Only available on hardware with individual temperature sensors, such as the VESC 75/300.",
        "°C。仅在具有独立温度传感器的硬件上可用，例如 VESC 75/300。",
    ),

    (
        "Motor temperature in ",
        "电机温度，单位为",
    ),

    (
        "Motor current in A. "
        "The sign is the same as the input current, thus positive when the motor is driving "
        "and negative when the motor is generating.",
        "电机电流，单位为 A。"
        "符号与输入电流相同，因此电机驱动时为正，电机发电时为负。",
    ),

    (
        "Input current in A.",
        "输入电流，单位为 A。",
    ),

    (
        "D-axis and Q-axis current of the motor. Only available in FOC mode.",
        "电机的 D 轴和 Q 轴电流。仅在 FOC 模式下可用。",
    ),

    (
        "Motor speed in electrical rouds per minute. "
        "Has to be divided by the number of pole pairs to get the mechanical speed.",
        "电机转速，单位为电气转速/分钟。"
        "必须除以极对数才能得到机械转速。",
    ),

    (
        "Modulation, range -1.0 to 1.0",
        "调制，范围 -1.0 到 1.0",
    ),

    (
        "Ampere hours consumed from the input.",
        "从输入端消耗的安培小时数。",
    ),

    (
        "Ampere hours fed back to the input.",
        "反馈到输入端的安培小时数。",
    ),

    (
        "Watt hours consumed from the input.",
        "从输入端消耗的瓦特小时数。",
    ),

    (
        "Watt hours fed back to the input.",
        "反馈到输入端的瓦特小时数。",
    ),

    (
        "1/6 electrical revolution counter. "
        "Will count 6 steps for every electrical revolution of the motor. "
        "Has to be multiplied by the number of pole pairs to get 6 times "
        "the counts per mechanical revolution. "
        "Will count backwards when the motor is turning backwards.",
        "1/6 电气转数计数器。"
        "电机每电气转一圈将计数 6 步。"
        "必须乘以极对数才能得到每机械转一圈的 6 倍计数。"
        "电机反转时将倒数。",
    ),

    (
        "Same as <span style=\" font-family:'Roboto';\">tachometer</span>"
        "<span style=\" font-family:'Roboto';\">, but couts the absolute value</span>",
        "与 <span style=\" font-family:'Roboto';\">tachometer</span>"
        "<span style=\" font-family:'Roboto';\"> 相同，但计数绝对值</span>",
    ),
    (
        "Same as <span style=\" font-weight:600;\">tachometer</span>, but couts the absolute value",
        "与 <span style=\" font-weight:600;\">tachometer</span> 相同，但计数绝对值",
    ),

    (
        "Motor position in degrees. "
        "It is the mechanical position when using an encoder, the electrical position otherwise. "
        "In sensorless mode the position is not valid when the motor is not turning.",
        "电机位置，单位为度。"
        "使用编码器时为机械位置，否则为电气位置。"
        "在无传感器模式下，电机不旋转时位置无效。",
    ),

    (
        "Current fault code.",
        "当前故障代码。",
    ),

    (
        "CAN ID of this VESC.",
        "此 VESC 的 CAN ID。",
    ),

    # ========================================================================
    # app_chuk.info (Nunchuk)
    # ========================================================================

    (
        "This app has been tested with the wireless Nyko Kama nunchuk. "
        "The receiver can be connected directly to the I2C port on the ESC. "
        "The y-axis on the joystick is used for acceleration/braking. "
        "The buttons have the following functions:",
        "此应用已通过无线 Nyko Kama nunchuk 测试。"
        "接收器可以直接连接到 ESC 上的 I2C 端口。"
        "摇杆的 Y 轴用于加速/制动。"
        "按钮具有以下功能：",
    ),

    (">C-Button:<", ">C 按钮：<"),
    (
        "Cruise control. "
        "If the C-button is pressed, the ESC will maintail the current speed with a PID control loop. "
        "The joystick can still be used to accelerate and brake, but as soon as it is returned "
        "to the center position the new speed will be maintained, as long as the C-button remains pressed.",
        "巡航控制。"
        "如果按下 C 按钮，ESC 将通过 PID 控制回路维持当前速度。"
        "摇杆仍可用于加速和制动，但只要返回到中心位置，新速度将被保持，直到 C 按钮保持按下状态。",
    ),

    (">Z-Button:<", ">Z 按钮：<"),
    (
        "The Z-button is used to change the direction of the motor if reverse is activated. "
        "Without reverse, Z has no effect.",
        "如果启用了反转，Z 按钮用于改变电机方向。"
        "如果没有反转，Z 按钮无效。",
    ),

    (
        "There is also a safety function. "
        "If nothing received from the nunchuk (including the accelerometers) changes for longer "
        "than the timeout value in the <span style=\" font-style:italic;\">APP General</span>"
        " page, the timeout function will be activated and either release the motor "
        "or brake with the current specified next to the timeout value.",
        "还有一个安全功能。"
        "如果从 nunchuk（包括加速度计）接收到的数据在超过"
        "<span style=\" font-style:italic;\">APP 通用</span>"
        "页面的超时值期间没有任何变化，超时功能将被激活，"
        "并释放电机或以超时值旁边指定的电流制动。",
    ),

    # ========================================================================
    # app_ppm_mapping_help
    # ========================================================================

    (
        "PPM pulselength mapping is used to map the minimum and maximum throttle values "
        "from the PPM remote to the minimum and maximum throttle values of the motor controller. "
        "The following procedure can be used:",
        "PPM 脉冲长度映射用于将 PPM 遥控器的最小和最大油门值映射到"
        "电机控制器的最小和最大油门值。可以使用以下步骤：",
    ),

    (
        "Activate the PPM app and write the configuration.",
        "激活 PPM 应用并写入配置。",
    ),
    (
        "Set the PPM control mode to disabled to avoid motor movement and write the configuration.",
        "将 PPM 控制模式设置为禁用，以避免电机移动，然后写入配置。",
    ),
    (
        "Connect the remote.",
        "连接遥控器。",
    ),
    (
        "Activate app realtime data streaming in the main toolbar. "
        "The input display should show the decoded input value and pulse length "
        "if the remote is connected and on.",
        "激活主工具栏中的应用实时数据流。"
        "如果遥控器已连接并开启，输入显示应显示解码后的输入值和脉冲长度。",
    ),
    (
        "Move the throttle between the minimum and maximum values to get them sampled.",
        "在最小值和最大值之间移动油门以进行采样。",
    ),
    (
        "Apply the result.",
        "应用结果。",
    ),
    (
        "Write the configuration.",
        "写入配置。",
    ),

    (
        "Input mapping should also be usable for those oneshot pulselengths that are popular "
        "for some multirotor flight controllers that don't have support for proper ESC communication "
        "such as CAN-bus or UART.",
        "输入映射也适用于某些多旋翼飞行控制器常用的单次脉冲长度，"
        "这些控制器不支持 CAN 总线或 UART 等适当的 ESC 通信。",
    ),

    # ========================================================================
    # app_adc_mapping_help
    # ========================================================================

    (
        "ADC voltage mapping is used to map the minimum and maximum throttle values "
        "from the analog throttle to the minimum and maximum throttle values of the motor controller. "
        "The following procedure can be used:",
        "ADC 电压映射用于将模拟油门的最小和最大油门值映射到"
        "电机控制器的最小和最大油门值。可以使用以下步骤：",
    ),

    (
        "Activate the ADC app and write the app configuration.",
        "激活 ADC 应用并写入应用配置。",
    ),
    (
        "Set the ADC control mode to disabled to avoid motor movement and write the configuration.",
        "将 ADC 控制模式设置为禁用，以避免电机移动，然后写入配置。",
    ),
    (
        "Connect the throttle(s).",
        "连接油门。",
    ),
    (
        "Activate realtime <span style=\" font-weight:600;\">app</span>"
        " data streaming in the main toolbar. "
        "The input displays should show the decoded input value and voltage if the throttle is connected.",
        "激活实时 <span style=\" font-weight:600;\">app</span>"
        " 主工具栏中的数据流。"
        "如果油门已连接，输入显示应显示解码后的输入值和电压。",
    ),
    (
        "Activate the desired control mode.",
        "激活所需的控制模式。",
    ),
    (
        "Write the app configuration.",
        "写入应用配置。",
    ),

    # ========================================================================
    # app_adc.info
    # ========================================================================

    (
        "The cruise control button will maintain the current speed while pressed when current control "
        "is used and no throttle is given. "
        "The reverse button is used to reverse the throttle when one of the corresponding control modes "
        "is used.",
        "当使用电流控制且未给油门时，按住巡航控制按钮将维持当前速度。"
        "当使用相应的控制模式之一时，反转按钮用于反转油门。",
    ),

    (
        "When only the ADC app is used, the TX pin is used for the cruise control button "
        "and the RX pin is used for the reverse button. "
        "When the ADC and UART apps are used at the same time, the servo input will be used as the button. "
        "In this case it will be used for the reverse button when a control mode with button is selected, "
        "otherwise it will be used for the cruise control button.",
        "仅使用 ADC 应用时，TX 引脚用于巡航控制按钮，RX 引脚用于反转按钮。"
        "同时使用 ADC 和 UART 应用时，伺服输入将用作按钮。"
        "在这种情况下，当选择了带按钮的控制模式时，它将用于反转按钮，否则用于巡航控制按钮。",
    ),

    # ========================================================================
    # wizard_startup_conclusion
    # ========================================================================

    (
        "You are now ready to start using VESC Tool. If you have any questions, visit ",
        "您现在可以开始使用 VESC Tool 了。如果您有任何问题，请访问 ",
    ),

    # ========================================================================
    # Generic
    # ========================================================================

    (
        "The firmware version(s) that this version of VESC Tool supports.",
        "此版本 VESC Tool 支持的固件版本。",
    ),
]


# ---------------------------------------------------------------------------
# Second-pass regex replacements for safe tag-level changes
# ---------------------------------------------------------------------------
TAG_SAFE_REPLACEMENTS = [
    # These patterns operate on text that may be INSIDE HTML tags.
    # Applied AFTER all exact string replacements so that
    # they do not interfere with multi-line exact matches.

    # Title "Motor Setup Wizard" — handles both font-weight and font-family variants
    (re.compile(r'>Motor Setup Wizard<'), '>电机设置向导<'),
    # Title "Input Setup Wizard"
    (re.compile(r'>Input Setup Wizard<'), '>输入设置向导<'),
    # Title "Stream realtime data"
    (re.compile(r'>Stream realtime data<'), '>流式传输实时数据<'),
    # Title "APP General" (italic span)
    (re.compile(r'>APP General<'), '>APP 通用<'),
    # Title "Apply" button
    (re.compile(r'>Apply<'), '>应用<'),
    # "very important" inside a color span
    (re.compile(r'>very important<'), '>非常重要<'),
    # "Description" inside tags
    (re.compile(r'>Description<'), '>描述<'),
    # "File" inside tags
    (re.compile(r'>File<'), '>文件<'),
    # Warning inside a span
    (re.compile(r'>Warning<'), '>警告<'),
]


def translate_html(raw_html):
    """Apply all translations to an HTML string. Returns the translated string."""
    result = raw_html

    # Pass 1: exact string replacements (long, specific patterns first)
    for eng, chn in TRANSLATIONS:
        if eng in result:
            result = result.replace(eng, chn)

    # Pass 2: regex replacements for tag-safe patterns
    for pattern, replacement in TAG_SAFE_REPLACEMENTS:
        result = pattern.sub(replacement, result)

    return result


def process_info_xml(filepath):
    """Process a single info.xml file: translate all <description> elements."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    changed = 0
    for elem in root.iter():
        if elem.tag == 'description':
            raw = elem.text
            if raw and raw.strip():
                translated = translate_html(raw)
                if translated != raw:
                    elem.text = translated
                    changed += 1

    if changed > 0:
        tree.write(filepath, encoding='UTF-8', xml_declaration=True)
        print(f"  Updated {changed} descriptions")

    return changed


def main():
    pattern = os.path.join(CONFIG_ROOT, "*", "info.xml")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No info.xml files found under {CONFIG_ROOT}")
        return

    print(f"Found {len(files)} info.xml files to process.\n")

    total_changed = 0
    total_files_changed = 0
    for filepath in files:
        version = os.path.basename(os.path.dirname(filepath))
        print(f"Processing v{version}...", end="")
        try:
            changed = process_info_xml(filepath)
            total_changed += changed
            if changed > 0:
                total_files_changed += 1
        except Exception as e:
            print(f" ERROR: {e}")

    print(f"\nDone. Total descriptions translated: {total_changed}")
    print(f"Total files with changes: {total_files_changed}")


if __name__ == '__main__':
    main()
