#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 100   // Change this to scale the experiment

// ---------- Utility ----------
void copy_array(int *src, int *dst, int n) {
    for (int i = 0; i < n; i++)
        dst[i] = src[i];
}

// ---------- Bubble Sort ----------
void bubble_sort(int *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

// ---------- Merge Sort ----------
void merge(int *arr, int l, int m, int r) {
    int n1 = m - l + 1;
    int n2 = r - m;

    int *L = malloc(n1 * sizeof(int));
    int *R = malloc(n2 * sizeof(int));

    for (int i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (int i = 0; i < n2; i++)
        R[i] = arr[m + 1 + i];

    int i = 0, j = 0, k = l;

    while (i < n1 && j < n2)
        arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];

    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];

    free(L);
    free(R);
}

void merge_sort(int *arr, int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        merge_sort(arr, l, m);
        merge_sort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}

// ---------- Quick Sort ----------
int partition(int *arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            int tmp = arr[i];
            arr[i] = arr[j];
            arr[j] = tmp;
        }
    }

    int tmp = arr[i + 1];
    arr[i + 1] = arr[high];
    arr[high] = tmp;

    return i + 1;
}

void quick_sort(int *arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

// ---------- Main ----------
int main() {
    srand(time(NULL));

    int *original = malloc(N * sizeof(int));
    int *arr = malloc(N * sizeof(int));

    // Generate random array
    for (int i = 0; i < N; i++)
        original[i] = rand();

    clock_t start, end;

    // Bubble Sort
    copy_array(original, arr, N);
    start = clock();
    bubble_sort(arr, N);
    end = clock();
    printf("Bubble Sort Time: %.6f seconds\n",
           (double)(end - start) / CLOCKS_PER_SEC);

    // Merge Sort
    copy_array(original, arr, N);
    start = clock();
    merge_sort(arr, 0, N - 1);
    end = clock();
    printf("Merge Sort Time: %.6f seconds\n",
           (double)(end - start) / CLOCKS_PER_SEC);

    // Quick Sort
    copy_array(original, arr, N);
    start = clock();
    quick_sort(arr, 0, N - 1);
    end = clock();
    printf("Quick Sort Time: %.6f seconds\n",
           (double)(end - start) / CLOCKS_PER_SEC);

    free(original);
    free(arr);

    return 0;
}
