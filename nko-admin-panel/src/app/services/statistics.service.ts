// statistics.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class StatisticsService {
  private apiUrl = environment.apiUrl + environment.endpoints.statistics;

  constructor(private http: HttpClient) { }

  getCompleteStatistics(includeAdvanced: boolean = false): Observable<StatisticsResponse> {
    return this.http.get<StatisticsResponse>(`${this.apiUrl}/?include_advanced=${includeAdvanced}`);
  }

  getBaseStatistics(): Observable<BaseStatsResponse> {
    return this.http.get<BaseStatsResponse>(`${this.apiUrl}/base`);
  }

  getPopularCategories(limit: number = 10): Observable<CategoryStats[]> {
    return this.http.get<CategoryStats[]>(`${this.apiUrl}/popular/categories?limit=${limit}`);
  }

  getPopularItems(limit: number = 10): Observable<PopularItem[]> {
    return this.http.get<PopularItem[]>(`${this.apiUrl}/popular/items?limit=${limit}`);
  }

  getAdvancedStatistics(): Observable<AdvancedStats> {
    return this.http.get<AdvancedStats>(`${this.apiUrl}/advanced`);
  }
}

export interface BaseStatsResponse {
  total_users: number;
  total_lessors: number;
  total_equipment: number;
  approved_bookings: number;
  rejected_bookings: number;
}

export interface CategoryStats {
  category_id: number;
  category_name: string | null;
  equipment_count: number;
  booking_count: number;
}

export interface PopularItem {
  equipment_id: number;
  equipment_name: string | null;
  booking_count: number;
  total_quantity_booked: number;
}

export interface AdvancedStats {
  avg_rental_duration_days: number | null;
  active_users_count: number;
  total_rental_days: number;
}

export interface StatisticsResponse {
  base_stats: BaseStatsResponse;
  popular_categories: CategoryStats[];
  popular_items: PopularItem[];
  advanced_stats?: AdvancedStats;
}