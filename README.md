# UnifiedGUI
## Summary
UnifiedGUI is an abstract implementation of a graphical user interface which can be used for a variety of different purposes in the context of molecular communication.
## Structure
## Quick Start Guide
1.
1.
1.

## Create a new transmitter

## Create a new encoder

## Create a new receiver
1. Choose a name for your receiver, e.g. "MyReceiver".
1. In the directory Models/Implementations/Receivers, create a new Python file with the **exact** name chosen in step 1, e.g. MyReceiver.py
1. Open the file created in step 2.
   1. Import the ReceiverInterface:   
    `from Models.Interfaces.ReceiverInterface import ReceiverInterface`
   1. Create a new class with the **exact** same name chosen in step 1, inheriting from Models.Interfaces.ReceiverInterface.ReceiverInterface, e.g.
      ```
      class MyReceiver(ReceiverInterface):
         def __init__(self):
           pass
      ```
   1. Implement the required functions.

For reference, you can have a look at the already implemented example receiver (`Models/Implementations/Receivers/ExampleReceiver.py`).

## Create a new decoder