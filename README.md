# Evolutionary Cognition: Hunter-Gatherer Visuospatial Task

An interactive cognitive experiment built in Python (Tkinter) to test the Hunter-Gatherer Theory of Spatial Sex Differences (Silverman & Eals, 1992). This software contrasts visuomotor precision and latency times across two dynamic tasks designed to isolate evolutionary selective pressures.

## Context & Hypotheses
Evolutionary psychology posits that prehistoric survival roles exerted distinct selective pressures on human brain development. This project digitizes that premise to evaluate two core hypotheses:
* **Gathering Phase (Feature Search):** Evaluates static visual discrimination and spatial memory by measuring the latency in finding a subtle target among static distractors.
* **Hunting Phase (Visuomotor Tracking):** Measures motor agility, reaction time, and trajectory interception of a fast-moving, erratic target.

## Software Architecture
The application relies on a modular State Controller pattern to ensure experimental purity:
* **Deterministic Randomization:** A unique seed generated per participant guarantees consistent exposure pools while avoiding carryover effects.
* **Automated Fatigue Management:** Mandatory rest periods (1 and 2 minutes) trigger automatically after a set number of trials to mitigate cognitive load.
* **Asynchronous Logging:** Secure, append-only data registration prevents data loss during execution.

## Installation & Execution
Requires **Python 3.x** and the standard `tkinter` library. No external dependencies are needed for the core experiment.

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/hunter-gatherer-task.git](https://github.com/YOUR_USERNAME/hunter-gatherer-task.git)
