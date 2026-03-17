# Cvyt
A simple, UI-based app that can process video/image input. It is primarily built with **opencv-python** support. The entire app functions as a desktop application using Python to create the UI and run the backend. Additional logic is dynamically imported using **importlib**, and each extra logic **module** is treated as a module. Each module follows a defined structure.

# How to start
Its up to you.

# Dependencies
As mentioned, the app uses **Python** with **PySide6** for the UI and backend, and **opencv-python** to support video/image processing.

# Format, distribution
For now, it is available only as raw Python source code.

# Support
It has been developed and tested on the Linux platform (Ubuntu 24).

# Extendetion
The app uses **modules**, with each module contained in a separate folder that includes a **widget** (PySide6) and associated **logic**. Each module is expected to have a **module_config.json** file, which provides detailed information about the module (such as description, etc.).
The **widget** is treated as the **main** file and should define a class.
For more information, refer to the **HOWTO.pdf** for detailed instructions.