import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Equipment {
  id?: number;
  name: string;
  user_id: number;
  category_id: number;
  is_approved: boolean;
  is_publish: boolean;
  description?: string;
  quantity: number;
  created_at?: string;
  latitude?: number;
  longitude?: number;
  display_status?: string;
}

export interface EquipmentListResponse {
  equipments: Equipment[];
  total: number;
  skip: number;
  limit: number;
}

export interface EquipmentUpdate {
  name?: string;
  category_id?: number;
  description?: string;
  quantity?: number;
  latitude?: number;
  longitude?: number;
  is_approved?: boolean;
  is_publish?: boolean;
}

export interface EquipmentSearchParams {
  category_id?: number;
  user_id?: number;
  is_approved?: boolean;
  is_publish?: boolean;
  name?: string;
}

@Injectable({
  providedIn: 'root'
})
export class EquipmentService {
  private baseUrl = environment.apiUrl + environment.endpoints.equipment;

  constructor(private http: HttpClient) {}

  // Получить список оборудования с пагинацией
  getEquipment(skip: number = 0, limit: number = 100): Observable<EquipmentListResponse> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    return this.http.get<EquipmentListResponse>(this.baseUrl, { params });
  }

  // Получить оборудование по ID
  getEquipmentById(equipmentId: number): Observable<Equipment> {
    return this.http.get<Equipment>(`${this.baseUrl}/${equipmentId}`);
  }

  // Создать оборудование
  createEquipment(equipmentData: Partial<Equipment>): Observable<Equipment> {
    return this.http.post<Equipment>(this.baseUrl, equipmentData);
  }

  // Обновить оборудование
  updateEquipment(equipmentId: number, equipmentData: EquipmentUpdate): Observable<Equipment> {
    return this.http.put<Equipment>(`${this.baseUrl}/${equipmentId}`, equipmentData);
  }

  // Удалить оборудование
  deleteEquipment(equipmentId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${equipmentId}`);
  }

  // Обновить статус одобрения
  updateApprovalStatus(equipmentId: number, isApproved: boolean): Observable<Equipment> {
    return this.http.patch<Equipment>(`${this.baseUrl}/${equipmentId}/approval`, { is_approved: isApproved });
  }

  // Обновить статус публикации
  updatePublishStatus(equipmentId: number, isPublish: boolean): Observable<Equipment> {
    return this.http.patch<Equipment>(`${this.baseUrl}/${equipmentId}/publish`, { is_publish: isPublish });
  }

  // Обновить количество
  updateQuantity(equipmentId: number, quantity: number): Observable<Equipment> {
    return this.http.patch<Equipment>(`${this.baseUrl}/${equipmentId}/quantity`, { quantity });
  }

  // Получить оборудование по владельцу
  getEquipmentByOwner(userId: number): Observable<Equipment[]> {
    return this.http.get<Equipment[]>(`${this.baseUrl}/user/${userId}`);
  }

  // Получить оборудование по категории
  getEquipmentByCategory(categoryId: number): Observable<Equipment[]> {
    return this.http.get<Equipment[]>(`${this.baseUrl}/category/${categoryId}`);
  }

  // Получить оборудование по статусу одобрения
  getEquipmentByApprovalStatus(isApproved: boolean): Observable<Equipment[]> {
    let params = new HttpParams().set('is_approved', isApproved.toString());
    return this.http.get<Equipment[]>(`${this.baseUrl}/status/approved`, { params });
  }

  // Получить оборудование по статусу публикации
  getEquipmentByPublishStatus(isPublish: boolean): Observable<Equipment[]> {
    let params = new HttpParams().set('is_publish', isPublish.toString());
    return this.http.get<Equipment[]>(`${this.baseUrl}/status/published`, { params });
  }

  // Поиск оборудования
  searchEquipment(searchParams: EquipmentSearchParams): Observable<Equipment[]> {
    return this.http.post<Equipment[]>(`${this.baseUrl}/search`, searchParams);
  }

  // Найти оборудование поблизости
  getEquipmentNearLocation(latitude: number, longitude: number, radiusKm: number = 10, limit: number = 100): Observable<Equipment[]> {
    let params = new HttpParams()
      .set('latitude', latitude.toString())
      .set('longitude', longitude.toString())
      .set('radius_km', radiusKm.toString())
      .set('limit', limit.toString());

    return this.http.get<Equipment[]>(`${this.baseUrl}/location/nearby`, { params });
  }
}