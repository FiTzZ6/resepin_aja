import matplotlib.pyplot as plt
import numpy as np

# Gabungkan epoch: Stage1 = 1..10, Stage2 = 11..15
epochs = np.arange(1, 16)
train_loss = [2.9693,1.3726,0.9114,0.7131,0.5716,0.4786,0.3983,0.3566,0.3136,0.2711,
              0.2042,0.1781,0.1722,0.1631,0.1517]
val_loss   = [1.7639,0.9925,0.8191,0.7404,0.6995,0.6699,0.6520,0.6335,0.6332,0.6199,
              0.6281,0.6325,0.6403,0.6430,0.6427]
train_acc  = [0.2668,0.6268,0.7514,0.8059,0.8447,0.8743,0.8954,0.9126,0.9206,0.9385,
              0.9556,0.9625,0.9614,0.9651,0.9693]
val_acc    = [0.6379,0.7629,0.7912,0.8106,0.8209,0.8312,0.8376,0.8415,0.8505,0.8505,
              0.8544,0.8570,0.8557,0.8557,0.8557]

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle('Kurva Training Gabungan — EfficientNetB0 Tanpa Augmentasi', fontweight='bold')

for ax, tr, vl, title, ylabel in [
    (axes[0], train_loss, val_loss, 'Loss', 'Loss'),
    (axes[1], train_acc,  val_acc,  'Accuracy', 'Accuracy')]:
    ax.plot(epochs, tr, 'o-', label=f'Train {title}', color='#1f77b4')
    ax.plot(epochs, vl, 's-', label=f'Val {title}',   color='#ff7f0e')
    ax.axvline(10.5, color='gray', linestyle='--', label='Stage 1 → Stage 2')
    ax.set_title(f'{title} (Stage 1 + Stage 2)')
    ax.set_xlabel('Epoch'); ax.set_ylabel(ylabel)
    ax.legend(); ax.grid(True, alpha=0.3)
    # anotasi nilai terbaik
    if title == 'Loss':
        best = int(np.argmin(vl)); ax.annotate(f'best val={vl[best]:.4f}',
            (epochs[best], vl[best]), textcoords='offset points', xytext=(10,-15), color='red')
    else:
        best = int(np.argmax(vl)); ax.annotate(f'best val={vl[best]:.4f}',
            (epochs[best], vl[best]), textcoords='offset points', xytext=(10,10), color='red')

plt.tight_layout()
plt.savefig('kurva_gabungan_tanpa_augmentasi.png', dpi=150, bbox_inches='tight')
print("✅ Tersimpan: kurva_gabungan_tanpa_augmentasi.png")
plt.show()