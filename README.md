# COMP361 Group Project
## Table of Contents

1. [Introduction](#1-introduction)
2. [Setup and Run](#2-setup-and-run)
3. [Instruction](#3-instruction)
4. [Citation](#4-citation)
5. [Contact](#5-contact)

## 1. Introduction

The Mars Terrain Simulator aims to address several critical challenges associated with Mars avatars, especially the challenges of navigation of the Martian surface. 
The simulator uses real mars terrain data collected by MRO(Mars Reconnaissance Orbiter) to provide accurate and detailed avatar simulation. 
Additionally, it features a modular brain system, allowing users to replace and test different pathfinding algorithms within the avatar. 
This flexibility enables comparative evaluation of various navigation strategies under realistic Martian conditions, enhancing research and development in autonomous planetary exploration. 
The simulator provides user-friendly interfaces and supports visualization of the simulation, allowing the users to learn and use the simulator with ease. 

The simulator may serve as a basic and valuable test for pathfinding algorithms in development or be used as a convenient teaching tool for algorithm design and evaluation. 
By providing an interactive and realistic simulation environment, the simulator allows students and researchers to explore various pathfinding, optimization, and decision-making algorithms in a controlled Martian terrain.

### Project Structure

```bash
COMP361/
├── controller/
├── model/
├── view/
├── run.py
├── reset_db.py
├── requirements.txt
├── main.py
└── README.md
```

## 2. Setup and Run

You can run the Mars AI Simulator locally by either **cloning the repository** or **downloading the project as a ZIP file**.

### Option 1: Clone the Repository

```bash
git clone https://github.com/VictorHe404/COMP361.git
cd COMP361
```
### Option 2: Download the ZIP

1. Download the zip for the project
2. Extract the contents and open the project folder

### Start the Application

Once the project is on your local machine, simply run:

```bash
python run.py
```

This command will:

Create a virtual environment (if one doesn't already exist)

Install all required dependencies from requirements.txt

Initialize the database by running reset_db.py

Launch the application using main.py

### Requirements

Python 3.11 (recommended) or 3.12 

## 3. Instruction

Command Line Interface for the Visualizer

The CLI for the visualizer follows a Linux-style structure:
Command Format: 
```bash
command [-flag(s)] [argument(s)]
```

If an undefined command is entered, the system returns: 
```bash
Error: Invalid command
```

If a command is used with invalid or missing arguments, a specific error message is returned.

Example Errors: 
```bash
move
moveCommandError: Destination not specified.

move [invalid destination]
moveCommandError: Invalid destination format: [invalid destination]
```

Flags: Flags allow users to modify or extend command functionality. Flags begin with a hyphen (-) and are placed before arguments.

Available Commands:
```bash
lmap
```
Description: Lists all available maps for the user to explore.

Usage Example:
```bash
lmap
[lmap] List of available maps:
  - Louth_Crater_Normal
  - Louth_Crater_Sharp
```
```bash
cavatar [avatarname]
```

Description: Creates a new avatar with the specified [avatarname].

Usage Example:
```bash
cavatar a1
[cavatar] Avatar 'a1' created successfully.
```

```bash
lavatar
```
Description: Lists all existing avatars for the user.

Usage Example:
```bash
lavatar
[lavatar] List of existing avatars:
  - a1
  - a10
```

```bash
savatar [avatarname]
```
Description: Sets the avatar named [avatarname] as the current avatar.

Usage Example:
```bash
savatar a1
[savatar] Avatar 'a1' set successfully.
```

```bash
lbrain
```
Description: Lists all available brains for the currently selected avatar.

Usage Example:

```bash
lbrain
[lbrain] List of available brains:
  - greedy
  - astar
```

```bash
sbrain [braintype]
```

Description: Sets the brain of the current avatar to [braintype].

Note: [braintype] must be one of the following (fixed choices): astar, greedy

Usage Example:
```bash
sbrain astar
[sbrain] Brain set successfully to astar.
```
```bash
stask [start_row] [start_column] [destination_row] [destination_column]
```
Description: Sets a task for the current avatar to move from (start_row, start_column) to (destination_row, destination_column).

```bash
run
```
Description: Executes the pre-set task assigned to the current avatar.

```bash
move -t [start_row] [start_column] [destination_row] [destination_column]
```
Description: Moves the current avatar from a starting position to a specified destination.

Usage Example:
```bash
move -t 20 20 35 45
Moves the avatar from (20, 20) to (35, 45).
```

```bash
report [-flag(s)]
```
Description: Generates a report about the current avatar and its status. Takes no arguments.

```bash
iavatar [avatarname]
```
Description: find a specific avatar by name and display its information. If the avatar is not found, an error message is displayed. If the [avatarname] is not specified, the currently selected avatar is used.

Usage Example:
```bash
iavatar
[iavatar] Info for currently selected avatar:[info]
iavatar a1
[iavatar] Info for avatar a1: [info]
```

## 4. Citation

## 5. Contact
