import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Equipment {
  id?: number;
  name: string;
  user_id: number;
  category_id: number;
  category_name: string;
  status: string; // 'moderation' | 'approved' | 'rejected'
  description?: string;
  quantity: number;
  created_at?: string;
  latitude?: number;
  longitude?: number;
  display_status?: string;
  rejection_reason?: string;
  moderated_at?: string;
  moderated_by?: number;
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
  status?: string;
}

export interface EquipmentSearchParams {
  category_id?: number;
  user_id?: number;
  status?: string;
  name?: string;
}

export interface EquipmentStats {
  total: number;
  moderation: number;
  approved: number;
  rejected: number;
}

@Injectable({
  providedIn: 'root'
})
export class EquipmentService {
  private baseUrl = environment.apiUrl + environment.endpoints.equipment;

  constructor(private http: HttpClient) {}

  getEquipment(
    skip: number = 0,
    limit: number = 100,
    status?: string
  ): Observable<EquipmentListResponse> {

    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<EquipmentListResponse>(this.baseUrl, { params });
  }

  approveEquipment(equipmentId: number): Observable<Equipment> {
    return this.http.patch<Equipment>(`${this.baseUrl}/${equipmentId}/approve`, {});
  }

  rejectEquipment(equipmentId: number, reason: string = ''): Observable<Equipment> {
    return this.http.patch<Equipment>(`${this.baseUrl}/${equipmentId}/reject`, { reason });
  }
}