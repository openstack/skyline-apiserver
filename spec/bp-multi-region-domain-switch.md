# BP: Multi Region & Domain Switch

## Problem

1. Skyline couldn't switch between multi-regions after login yet, user have to select region during login step. It's not good.
2. Skyline couldn't switch between domain also.

## Solution Draft

1. Remove region selection item in login page.
2. Remove domain selection item in login page. Users have to type in their domains during login step. Default domain is 'Default'.
3. After users login, they can switch region by select region name/id on the top of the web console page
4. After users login, they can switch domain if they had been assigned other domain resources
