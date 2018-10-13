Assignment 5.1

AIM: Implement activity selection problem

CODE: 

// C++ program for activity selection problem. 
// The following implementation assumes that the activities 
// are already sorted according to their finish time 
#include<stdio.h> 
  
// Prints a maximum set of activities that can be done by a single 
// person, one at a time. 
//  n   -->  Total number of activities 
//  s[] -->  An array that contains start time of all activities 
//  f[] -->  An array that contains finish time of all activities 
void printMaxActivities(int s[], int f[], int n) 
{ 
    int i, j; 
  
    printf ("Following activities are selected:\n"); 
  
    // The first activity always gets selected 
    i = 0; 
    printf("%d ", i); 
  
    // Consider rest of the activities 
    for (j = 1; j < n; j++) 
    { 
      // If this activity has start time greater than or 
      // equal to the finish time of previously selected 
      // activity, then select it 
      if (s[j] >= f[i]) 
      { 
          printf ("%d ", j); 
          i = j; 
      } 
    } 
    printf("\n");
} 
  
// driver program to test above function 
int main() 
{ 
    int s[] =  {1, 1, 0, 3, 4, 4, 5, 2}; 
    int f[] =  {2, 3, 4, 5, 5, 6, 8, 9}; 
    int n = sizeof(s)/sizeof(s[0]); 
    printMaxActivities(s, f, n); 
    return 0; 
} 

OUTPUT:

Following activities are selected:
0 3 6 

DISCUSSION:

It takes O(n) time when it is given that input activities are always sorted.