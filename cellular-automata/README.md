Cellular Automata — Animal Kingdom

A Python simulation built with pygame and numpy, modeling a predator-prey ecosystem on a grid using cellular automata.
This was a group course assignment for Scientific Computing at Roskilde University, completed together with Fabrizio Rodriguez and Juan Lovotti. The base simulation modeled fish and bears interacting on a grid:

- Fish breed, die if overcrowded by other fish, and move to empty neighboring cells
- Bears die of starvation if they don't eat, breed when conditions allow, eat neighboring fish, and move
- The two species need to stay in balance, too many fish leads to bear overpopulation, too few leads to bear starvation

Extension (self-designed):

As the main extension, we introduced a third species, the piranhas, to study how adding a new predator affects the ecosystem's balance:

- Piranhas eat either fish or bears from neighboring cells (fish preferred), gaining "stomach" points for each (fewer for fish, more for bears)
- If a piranha's stomach exceeds a set limit, it dies
- Otherwise, it moves to an empty neighboring cell
  
The simulation was tested by isolating variables, reducing the grid to one animal of each type, slowing down the frame rate, and tracking individual agents step by step, to verify that breeding, starvation, and movement rules behaved as intended.

How to Run

Requirements:
- Python 3.x
- pygame and numpy libraries

Install dependencies:
pip install pygame numpy

Run the simulation:
python cellular_automata_piranha.py

