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

## 4. Citation

## 5. Contact
