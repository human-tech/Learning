#include <math.h>

#include "helpers.h"

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float sum = image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed;
            int avg = round(sum / 3);
            image[i][j].rgbtBlue = avg;
            image[i][j].rgbtGreen = avg;
            image[i][j].rgbtRed = avg;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        int n = width - 1;
        for (int j = 0; j < n; j++)
        {
            RGBTRIPLE imageswap;

            imageswap = image[i][j];
            image[i][j] = image[i][n];
            image[i][n] = imageswap;
            n--;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE imagecopy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int x = 0;
            float sumB = 0, sumG = 0, sumR = 0;
            for (int m = -1; m < 2; m++)
            {
                for (int n = -1; n < 2; n++)
                {
                    if (i + m > height - 1 || i + m < 0 || j + n > width - 1 || j + n < 0)
                    {
                        continue;
                    }
                    else
                    {
                        sumB += image[i + m][j + n].rgbtBlue;
                        sumG += image[i + m][j + n].rgbtGreen;
                        sumR += image[i + m][j + n].rgbtRed;
                        x++;
                    }
                }
            }
            imagecopy[i][j].rgbtBlue = round(sumB / x);
            imagecopy[i][j].rgbtGreen = round(sumG / x);
            imagecopy[i][j].rgbtRed = round(sumR / x);
        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = imagecopy[i][j];
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE imagecopy[height][width];
    
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float GxB = 0, GxG = 0, GxR = 0, GyB = 0, GyG = 0, GyR = 0;
            float sobel[3][3] =
            {
                {-1, 0, 1},
                {-2, 0, 2},
                {-1, 0, 1}
            };

            for (int m = -1; m < 2; m++)
            {
                for (int n = -1; n < 2; n++)
                {
                    if (i + m > height - 1 || i + m < 0 || j + n > width - 1 || j + n < 0)
                    {
                        continue;
                    }
                    else
                    {
                        GxB += image[i + m][j + n].rgbtBlue * sobel[m + 1][n + 1];
                        GxG += image[i + m][j + n].rgbtGreen * sobel[m + 1][n + 1];
                        GxR += image[i + m][j + n].rgbtRed * sobel[m + 1][n + 1];

                        GyB += image[i + m][j + n].rgbtBlue * sobel[n + 1][m + 1];
                        GyG += image[i + m][j + n].rgbtGreen * sobel[n + 1][m + 1];
                        GyR += image[i + m][j + n].rgbtRed * sobel[n + 1][m + 1];
                    }
                }
            }

            int B = round(sqrt(pow(GxB, 2) + pow(GyB, 2)));
            int G = round(sqrt(pow(GxG, 2) + pow(GyG, 2)));
            int R = round(sqrt(pow(GxR, 2) + pow(GyR, 2)));

            if (B > 255)
            {
                B = 255;
            }
            if (G > 255)
            {
                G = 255;
            }
            if (R > 255)
            {
                R = 255;
            }

            if (B < 0)
            {
                B = 0;
            }
            if (G < 0)
            {
                G = 0;
            }
            if (R < 0)
            {
                R = 0;
            }

            imagecopy[i][j].rgbtBlue = B;
            imagecopy[i][j].rgbtGreen = G;
            imagecopy[i][j].rgbtRed = R;
        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = imagecopy[i][j];
        }
    }
    return;
}
