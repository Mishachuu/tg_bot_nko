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
  currentImageIndex: number = 0;
  isLoading: boolean = false;
  imageErrorIds: Set<number> = new Set();

  constructor(
    public dialogRef: MatDialogRef<EquipmentPhotosDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EquipmentPhotosDialogData,
    private equipmentPhotoService: EquipmentPhotoService
  ) {}

  ngOnInit(): void {
    this.loadPhotos();
  }

  loadPhotos(): void {
    this.isLoading = true;
    this.equipmentPhotoService.getPhotosByEquipmentId(this.data.equipmentId)
      .subscribe({
        next: (response) => {
          this.photos = response.photos;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading photos:', error);
          this.isLoading = false;
        }
      });
  }

  getCurrentImageUrl(): string {
    if (this.photos.length === 0) return '';
    
    const currentPhoto = this.photos[this.currentImageIndex];
    return this.equipmentPhotoService.getPhotoImageUrl(currentPhoto.id);
  }

  handleImageError(event: any): void {
    const currentPhoto = this.photos[this.currentImageIndex];
    if (currentPhoto) {
      this.imageErrorIds.add(currentPhoto.id);
    }
  }

  hasImageError(photoId: number): boolean {
    return this.imageErrorIds.has(photoId);
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
    this.dialogRef.close();
  }
}