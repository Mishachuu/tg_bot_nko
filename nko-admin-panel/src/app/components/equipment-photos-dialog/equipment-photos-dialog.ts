// app/components/equipment-photos-dialog/equipment-photos-dialog.component.ts
import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { EquipmentPhoto, EquipmentPhotoService } from '../../services/equipment-photo.service';

export interface EquipmentPhotosDialogData {
  equipmentId: number;
  equipmentName: string;
}

@Component({
  selector: 'app-equipment-photos-dialog',
  templateUrl: './equipment-photos-dialog.html',
  styleUrls: ['./equipment-photos-dialog.scss'],
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ]
})
export class EquipmentPhotosDialogComponent implements OnInit {
  photos: EquipmentPhoto[] = [];
  loadedImages: { [key: number]: string } = {}; // blob URLs для изображений
  imageErrors: { [key: number]: boolean } = {}; // отслеживание ошибок загрузки изображений
  isLoading = true;
  currentImageIndex = 0;

  constructor(
    public dialogRef: MatDialogRef<EquipmentPhotosDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EquipmentPhotosDialogData,
    private photoService: EquipmentPhotoService
  ) {}

  ngOnInit(): void {
    this.loadPhotos();
  }

  loadPhotos(): void {
    this.isLoading = true;
    this.photoService.getPhotosByEquipmentId(this.data.equipmentId)
      .subscribe({
        next: (response) => {
          this.photos = response.photos;
          this.loadPhotoContents();
        },
        error: (error) => {
          console.error('Error loading photos:', error);
          this.isLoading = false;
        }
      });
  }

  loadPhotoContents(): void {
    if (this.photos.length === 0) {
      this.isLoading = false;
      return;
    }

    let loadedCount = 0;
    this.photos.forEach((photo, index) => {
      this.photoService.getPhotoById(photo.id)
        .subscribe({
          next: (photoWithContent) => {
            // Предполагаем, что content приходит как base64 строка
            if (photoWithContent.content) {
              try {
                this.loadedImages[photo.id] = this.photoService.base64ToBlobUrl(photoWithContent.content);
              } catch (error) {
                console.error('Error creating blob URL:', error);
                this.imageErrors[photo.id] = true;
              }
            } else {
              this.imageErrors[photo.id] = true;
            }
            loadedCount++;
            
            if (loadedCount === this.photos.length) {
              this.isLoading = false;
            }
          },
          error: (error) => {
            console.error('Error loading photo content:', error);
            this.imageErrors[photo.id] = true;
            loadedCount++;
            
            if (loadedCount === this.photos.length) {
              this.isLoading = false;
            }
          }
        });
    });
  }

  getCurrentImageUrl(): string {
    if (this.photos.length === 0) return '';
    const currentPhoto = this.photos[this.currentImageIndex];
    return this.loadedImages[currentPhoto.id] || '';
  }

  hasImageError(photoId: number): boolean {
    return this.imageErrors[photoId] === true;
  }

  // Метод для обработки ошибок загрузки изображения
  handleImageError(event: Event): void {
    const imgElement = event.target as HTMLImageElement;
    const currentPhoto = this.photos[this.currentImageIndex];
    
    if (currentPhoto) {
      this.imageErrors[currentPhoto.id] = true;
      
      // Показываем placeholder вместо сломанного изображения
      imgElement.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmNWY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPs6Vz4HOv8+Fzr/PgiDPhM6xz4HOv8+Fzr/PhTwvdGV4dD48L3N2Zz4=';
      imgElement.alt = 'Ошибка загрузки изображения';
    }
  }

  nextImage(): void {
    if (this.currentImageIndex < this.photos.length - 1) {
      this.currentImageIndex++;
    }
  }

  previousImage(): void {
    if (this.currentImageIndex > 0) {
      this.currentImageIndex--;
    }
  }

  close(): void {
    // Очищаем blob URLs чтобы избежать утечек памяти
    Object.values(this.loadedImages).forEach(url => {
      if (url && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
      }
    });
    this.dialogRef.close();
  }
}