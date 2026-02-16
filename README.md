# Cvyt
Simple app, Ui based which can be used to to process video/image input. I basic it has **opencv-python** support. The whole app works as desktop app using python to create UI and running backend. Extra logic is imported dynamically by **importlib**. Each extra logic is handled as **module**. Each **module** has defined structure.

# How to start
Its up to you.

# Dependencies
As been mentined its using **python** + **pyside6** for UI/backend and it has **opencv-python** to support video/image processing.

# Format, distribution
For now its available only in raw python source code form.

# Support
Its been developed and tested on Linux platform(ubuntu 24).

# Extendetion
App is using **modules**, folder for each contains **widget**(pyside6) and **logic**. Of course we are expecting **module_config.json** with detailed info about module(description, etc.)
The **widget** is handled as **main** file and it should contains class. 
For more info look to **HOWTO.pdf** for detailed info.