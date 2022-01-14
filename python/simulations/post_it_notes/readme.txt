Post-it simulations: An Experiment by Ziqing Ye
Written for fun on Dec 30, 2021

Background: post-it note flags are designed in an Nx2 matrix: N rows of stickers,
each row consisted of two different colors, one on each side. In each row,
only one color will be flipped up for pulling while the other was hidden below,
and the available color alternates. Once you pull out a sheet of color A, 
a sheet of color B will pop up, etc.
- Specifically I am refering to this type linked here:
https://www.walmart.com/ip/Post-it-Flags-5-in-Wide-Assorted-Colors-60-Flags/22478094

Goal: Try to use the colors as evenly as possible
Assumptions: After the first few pulls, you start to forget which rows are one pull
ahead and which rows haven't been pulled. You cannot tell based on thickness, and you
do not remember anything about your last pulls.
Hypothesis: certain ways of pulling yields a higher chance of ending up with an even
pull than other ways.
Definition: "even pull" means ending up with an even usage, meaning when one color is
used up, the other colors have at most 1 sheet left.

Methodology:
Have an Nx2 matrix to represent the post-it packet
Each matrix position contains a counter (the remaining sheets count) and a boolean
that reflects the state of the sheets pile (whether it is available for pulling)

Basic rules:
1. Each row contains exactly two piles.
2. In each and every row, there is exactly one pullable (P) pile and exactly one
unpullable (x) pile (cannot be the same pile).
3. only piles marked "P" are can be pulled from. After one pull, the pile's remaining
sheet count decrements by 1, and that pile's status became "x" (unpullable). On the
other hand, the opposite pile in the same row become "P" (pullable).
4. When a post-it packet is first created, every pile has the same number of sheets,
and the pullable ("P") tabs are all on the same (say left) side.
E.g.
P x
x P
P x
As long as those base rules are obeyed, we can create arbitrary post-it notes with
arbitrary (even) number of colors and sheet counts.

Findings: there does not seem to be a good way to pull stickers perfectly evenly.
While writing this class, I realized that it never mattered which column one pulls
from; the only parameter of concern is the row. However, if it is independent
of the column, then there is no longer a way to distinguish between different choices
by looking at e.g. the exact arrangement of "up" tabs. 
