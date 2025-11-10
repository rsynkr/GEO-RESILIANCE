"""
Debug helper functions to diagnose analysis issues
"""

import numpy as np

def print_mask_stats(mask, name="mask"):
    """Print statistics about a boolean mask"""
    print(f"\n{name} Statistics:")
    print(f"  Shape: {mask.shape}")
    print(f"  Total pixels: {mask.size}")
    print(f"  True pixels: {np.sum(mask)}")
    print(f"  False pixels: {np.sum(~mask)}")
    print(f"  Percentage True: {100 * np.sum(mask) / mask.size:.2f}%")
    if np.any(mask):
        print(f"  Has valid areas: YES")
    else:
        print(f"  Has valid areas: NO (all False)")

def print_array_stats(arr, name="array"):
    """Print statistics about a numpy array"""
    print(f"\n{name} Statistics:")
    print(f"  Shape: {arr.shape}")
    print(f"  Min: {np.nanmin(arr):.4f}")
    print(f"  Max: {np.nanmax(arr):.4f}")
    print(f"  Mean: {np.nanmean(arr):.4f}")
    print(f"  Std: {np.nanstd(arr):.4f}")

