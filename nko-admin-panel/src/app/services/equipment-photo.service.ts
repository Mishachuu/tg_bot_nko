// app/services/equipment-photo.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface EquipmentPhoto {
  id: number;
  equipment_id: number;
  filename: string;
  content?: string; // base64 encoded image
}

export interface EquipmentPhotoWithContent extends EquipmentPhoto {
  content: string; // base64 encoded image
}

export interface EquipmentPhotoListResponse {
  photos: EquipmentPhoto[];
  total: number;
  equipment_id: number;
}

export interface EquipmentPhotoCreate {
  equipment_id: number;
  filename: string;
  content: string; // base64 encoded image
}

@Injectable({
  providedIn: 'root'
})
export class EquipmentPhotoService {
  private baseUrl = environment.apiUrl + '/equipment-photos';

  constructor(private http: HttpClient) {}

  getPhotosByEquipmentId(equipmentId: number): Observable<EquipmentPhotoListResponse> {
    return this.http.get<EquipmentPhotoListResponse>(`${this.baseUrl}/equipment/${equipmentId}`);
  }

  getPhotoById(photoId: number): Observable<EquipmentPhotoWithContent> {
    return this.http.get<EquipmentPhotoWithContent>(`${this.baseUrl}/${photoId}`);
  }

  addPhoto(photoData: EquipmentPhotoCreate): Observable<EquipmentPhoto> {
    return this.http.post<EquipmentPhoto>(this.baseUrl, photoData);
  }

  deletePhoto(photoId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${photoId}`);
  }

  // Вспомогательный метод для преобразования base64 в blob URL
  base64ToBlobUrl(base64: string, contentType: string = 'image/jpeg'): string {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: contentType });
    return URL.createObjectURL(blob);
  }
}