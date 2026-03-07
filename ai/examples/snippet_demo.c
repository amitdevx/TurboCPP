/* TurboCPP AI Snippet Demo */
/* This shows how @ai works INSIDE existing code */

#include <stdio.h>
#include <conio.h>

void main()
{
    int arr[10], n, i;

    clrscr();

    printf("Enter number of elements (max 10): ");
    scanf("%d", &n);

    printf("Enter %d elements:\n", n);
    for (i = 0; i < n; i++)
        scanf("%d", &arr[i]);

    /* @ai sort this array using bubble sort and print the sorted result */

    getch();
}
