import os
import torchaudio
import torchaudio.transforms as T
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

def extract_sonority(audio_file_test, n_fft=2048, win_length=1024, hop_length=512, n_mels=20, plot_graphs=True):
    '''
    Extracts sonority values from the given audio file using Mel spectrogram analysis.

    Parameters:
    ----------
    audio_file_test : str
        Path to the input audio file.
    n_fft : int, optional
        Size of the FFT window (default is 2048).
    win_length : int, optional
        Window length for each frame in the STFT (default is 1024).
    hop_length : int, optional
        Hop length between STFT frames (default is 512).
    n_mels : int, optional
        Number of Mel frequency bands (default is 20).
    plot_graphs : bool, optional
        Whether to plot the Mel spectrogram and other results (default is True).

    Returns:
    -------
    avg_product_new : np.ndarray
        The average product of sub-band energies after applying smoothing.
    avg_product_time_new : np.ndarray
        The time values corresponding to the `avg_product_new`.
    '''
    # Load audio file
    waveform, sample_rate = torchaudio.load(audio_file_test)

    # Create the Mel filter bank for 250-3000Hz range
    mel_filterbank = T.MelSpectrogram(
        sample_rate=sample_rate,
        n_fft=n_fft,
        win_length=win_length,
        hop_length=hop_length,
        n_mels=n_mels,
        f_min=250.0,  # Start frequency (250 Hz)
        f_max=2500.0  # End frequency (2500 Hz)
    )

    # Apply the Mel filter bank to waveform
    mel_spectrogram = mel_filterbank(waveform)

    # Convert to decibels for visualization
    mel_spectrogram_db = T.AmplitudeToDB()(mel_spectrogram)

    # Compute temporal correlation (TCSSBC)
    def temporal_correlation(mel_spectrogram):
        mel_spectrogram_np = mel_spectrogram.squeeze().numpy()
        return np.corrcoef(mel_spectrogram_np)

    tcssbc_output = temporal_correlation(mel_spectrogram_db)

    # Min-max normalization helper
    def normalize_values(arr):
        return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

    # Compute energy envelope for each Mel band
    def compute_band_energies(mel_spec_db):
        mel_spec_np = mel_spec_db.squeeze().numpy()
        # Normalize and square energies
        normalized = np.array([normalize_values(band) for band in mel_spec_np])
        return normalized ** 2

    # Average product of pairs with TCSSBC modifier
    def average_product_of_pairs(energies, tcssbc):
        N = energies.shape[0]
        M = N * (N - 1) // 2
        avg_prod = np.zeros(energies.shape[1])
        for i in range(N):
            for j in range(i + 1, N):
                avg_prod += (energies[i] * energies[j]) * tcssbc[i, j]
        return avg_prod / M

    # Plotting helper
    def visualize_results(mel_db, tcssbc, avg_product, sr, hop):
        num_frames = mel_db.shape[-1]
        times = np.linspace(0, num_frames * hop / sr, num_frames)
        plt.figure(figsize=(12, 6))
        ax1 = plt.subplot(2, 1, 1)
        im1 = ax1.imshow(mel_db.squeeze(0).numpy(), origin='lower', aspect='auto', cmap='gray_r', extent=[0, times[-1], 0, mel_db.shape[0]])
        plt.colorbar(im1, ax=ax1, format='%+2.0f dB')
        ax1.set_title('Mel Spectrogram (250-2500Hz)')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Mel Band')

        ax2 = plt.subplot(2, 1, 2)
        im2 = ax2.imshow(tcssbc, aspect='auto', cmap='inferno')
        plt.colorbar(im2, ax=ax2)
        ax2.set_title('Temporal Correlation (TCSSBC)')
        ax2.set_xlabel('Band Index')
        ax2.set_ylabel('Band Index')

        twin = ax1.twinx()
        prod_times = np.linspace(0, (len(avg_product)-1) * hop / sr, len(avg_product))
        twin.plot(prod_times, avg_product, label='Avg Sub-band Product', color='#FFA500')
        twin.set_ylabel('Average Product')
        twin.legend(loc='upper right')

        plt.tight_layout()
        #plt.show()
        output_name = os.path.splitext(os.path.basename(audio_file_test))[0] + '_sonority.png'
        plt.savefig(output_name)
        plt.close()

    # Main processing
    squared_energies = compute_band_energies(mel_spectrogram_db)
    avg_product = average_product_of_pairs(squared_energies, tcssbc_output)
    times = np.linspace(0, (len(avg_product)-1) * hop_length / sample_rate, len(avg_product))
    # Interpolate to 0.005s steps
    new_times = np.arange(times[0], times[-1], 0.005)
    interp = np.interp(new_times, times, avg_product)
    smooth = gaussian_filter1d(interp, sigma=2)
    if plot_graphs:
        visualize_results(mel_spectrogram_db, tcssbc_output, avg_product, sample_rate, hop_length)
    return smooth, new_times


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract sonority from an audio file.")
    parser.add_argument("audio_file", help="Path to the input audio file")
    parser.add_argument("--n_fft", type=int, default=2048, help="FFT size")
    parser.add_argument("--win_length", type=int, default=1024, help="Window length")
    parser.add_argument("--hop_length", type=int, default=512, help="Hop length")
    parser.add_argument("--n_mels", type=int, default=20, help="Number of Mel bands")
    parser.add_argument("--no_plot", dest="plot_graphs", action="store_false", help="Disable plotting of graphs")
    args = parser.parse_args()

    sonority_vals, sonority_times = extract_sonority(
        args.audio_file,
        n_fft=args.n_fft,
        win_length=args.win_length,
        hop_length=args.hop_length,
        n_mels=args.n_mels,
        plot_graphs=args.plot_graphs
    )
    # Print summary of output
    print(f"Extracted {len(sonority_vals)} sonority values.")
