// Implements a dictionary's functionality

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stddef.h>
#include <ctype.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

unsigned int loaded = 0;

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 17576;

// Hash table
node *table[N] = {NULL};

void freeup(node *list);

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    for (node *tmp = table[hash(word)]; tmp != NULL; tmp = tmp->next)
    {
        if (strcasecmp(tmp->word, word) == 0)
        {
            return true;
        }
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    char a = toupper(word[0]);
    int x = a - 65;

    for (int i = 1; i < 3; i++)
    {
        if (strcmp(&word[i], "\0") == 0)
        {
            break;
        }

        (x == 0) ? x++ : x;
        a = toupper(word[i]);
        x = (x * 26) + a - 65;
    }
    return x;
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    FILE *dictfile = fopen(dictionary, "r");
    if (dictfile == NULL)
    {
        printf("Could not open %s.\n", dictionary);
        return false;
    }

    while (true)
    {
        char word[LENGTH + 1];
        unsigned int check = fscanf(dictfile, "%s", word);
        if (check == EOF)
        {
            break;
        }

        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }
        strcpy(n->word, word);
        n->next = NULL;

        unsigned int index = hash(word);

        n->next = table[index];
        table[index] = n;
        loaded++;
    }

    fclose(dictfile);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return loaded;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        freeup(table[i]);
    }
    return true;
}

void freeup(node *list)
{
    if (list == NULL)
    {
        return;
    }

    freeup(list->next);
    free(list);
    return;
}
