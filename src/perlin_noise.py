# perlin_noise.py
import numpy as np
import random

class Perlin:
    """
    Generates 2D Perlin noise.
    """
    def __init__(self):
        """
        Initializes the Perlin noise generator with a shuffled permutation table.
        """
        p_range = list(range(256))
        random.shuffle(p_range)
        self.p = np.array(p_range + p_range, dtype=int) # Double the permutation table

    def _fade(self, t: np.ndarray) -> np.ndarray:
        """
        Computes the fade function 6t^5 - 15t^4 + 10t^3.
        Args:
            t: Input array.
        Returns:
            Array after applying the fade function.
        """
        return t*t*t*(t*(t*6-15)+10)

    def _lerp(self, a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
        """
        Linear interpolation between a and b using t.
        Args:
            a: Start value(s).
            b: End value(s).
            t: Interpolation factor(s).
        Returns:
            Interpolated value(s).
        """
        return a + t*(b-a)

    def _grad(self, h: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Computes the gradient vector based on hash value h and coordinates x, y.
        This is a vectorized version.
        Args:
            h: Hash values.
            x: X coordinates.
            y: Y coordinates.
        Returns:
            Dot product of gradient and (x,y).
        """
        h_mod = h & 3  # Equivalent to h % 4
        u = np.where(h_mod < 2, x, y)
        v = np.where(h_mod < 2, y, x)

        part1 = np.where((h & 1) == 0, u, -u)
        part2 = np.where((h & 2) == 0, v, -v)
        return part1 + part2

    def noise_array(self, w: int, h: int, scale: float) -> np.ndarray:
        """
        Generates a 2D Perlin noise array.
        Args:
            w: Width of the noise array.
            h: Height of the noise array.
            scale: Scale factor for the noise coordinates. Smaller values zoom in.
                   Value must be positive.
        Returns:
            A 2D numpy array with noise values normalized between 0.0 and 1.0.
        """
        if scale <= 0:
            scale = 0.001 # Prevent division by zero or invalid scale

        # Generate coordinate arrays
        xs = np.linspace(0, w/scale, w, endpoint=False)
        ys = np.linspace(0, h/scale, h, endpoint=False)

        # Integer and fractional parts of coordinates
        xi0 = xs.astype(int)
        yi0 = ys.astype(int)
        xf0 = xs - xi0
        yf0 = ys - yi0
        xf1 = xf0 - 1.0
        yf1 = yf0 - 1.0

        # Fade curves for fractional parts
        u = self._fade(xf0) # For x-interpolation
        v_fade = self._fade(yf0) # For y-interpolation (per row)

        # Permutation table (already doubled)
        perm = self.p
        
        # Ensure integer coordinates are within permutation table's single range [0, 255]
        # for direct indexing, as values from perm table are used as indices.
        xi0_mod = xi0 & 255
        yi0_mod = yi0 & 255
        
        noise_map = np.empty((h, w), dtype=float)

        for j in range(h):
            # Calculate gradients for the four corners of the grid cell
            # Indices for permutation table (p is already doubled, so idx+1 is fine)
            # Top-left corner gradient index
            idx00 = perm[xi0_mod] + yi0_mod[j]
            # Top-right corner gradient index
            idx10 = perm[xi0_mod + 1] + yi0_mod[j]
            # Bottom-left corner gradient index
            idx01 = perm[xi0_mod] + yi0_mod[j] + 1
            # Bottom-right corner gradient index
            idx11 = perm[xi0_mod + 1] + yi0_mod[j] + 1
            
            # Hash values from permutation table to select gradients
            g00 = perm[idx00]
            g10 = perm[idx10]
            g01 = perm[idx01]
            g11 = perm[idx11]

            # Calculate dot products of gradient vectors and distance vectors
            n00 = self._grad(g00, xf0, yf0[j])
            n10 = self._grad(g10, xf1, yf0[j]) # xf - 1
            n01 = self._grad(g01, xf0, yf1[j]) # yf - 1
            n11 = self._grad(g11, xf1, yf1[j]) # xf - 1, yf - 1

            # Interpolate along x-axis
            x_interp1 = self._lerp(n00, n10, u)
            x_interp2 = self._lerp(n01, n11, u)
            
            # Interpolate along y-axis (using v_fade for the current row j)
            noise_map[j] = (self._lerp(x_interp1, x_interp2, v_fade[j]) + 1) * 0.5  # Normalize to [0, 1]
            
        return noise_map