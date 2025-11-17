import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  id?: number;
  tg_id: number;
  name: string;
  email?: string;
  phone_number?: string;
  is_lessor?: boolean;
  score?: number;
  created_at?: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  skip: number;
  limit: number;
}

export interface UserUpdate {
  name?: string;
  email?: string;
  phone_number?: string;
  is_lessor?: boolean;
  score?: number;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseUrl = environment.apiUrl + environment.endpoints.users;

  constructor(private http: HttpClient) {}

  // Получить список пользователей с пагинацией
  getUsers(skip: number = 0, limit: number = 100, isLessor?: boolean): Observable<UserListResponse> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    // Добавляем параметр фильтрации если он указан
    if (isLessor !== undefined) {
      params = params.set('is_lessor', isLessor.toString());
    }

    return this.http.get<UserListResponse>(this.baseUrl, { params });
  }

  // Получить пользователя по ID
  getUserById(userId: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${userId}`);
  }

  // Получить пользователя по Telegram ID
  getUserByTelegram(tgId: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/telegram/${tgId}`);
  }

  // Проверить существование пользователя по Telegram ID
  checkUserExists(tgId: number): Observable<{ exists: boolean }> {
    return this.http.get<{ exists: boolean }>(`${this.baseUrl}/telegram/${tgId}/exists`);
  }

  // Создать пользователя
  createUser(userData: Partial<User>): Observable<User> {
    return this.http.post<User>(this.baseUrl, userData);
  }

  // Создать пользователя со статусом арендодателя
  createUserWithLessor(userData: Partial<User>): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/with-lessor`, userData);
  }

  // Обновить пользователя
  updateUser(userId: number, userData: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/${userId}`, userData);
  }

  // Удалить пользователя
  deleteUser(userId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${userId}`);
  }

  // Обновить рейтинг пользователя
  updateUserScore(userId: number, score: number): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/${userId}/score`, { score });
  }

  // Обновить статус арендодателя
  updateLessorStatus(userId: number, isLessor: boolean): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/${userId}/lessor-status`, { is_lessor: isLessor });
  }

  // Поиск пользователей по имени
  searchUsersByName(query: string): Observable<User[]> {
    let params = new HttpParams().set('query', query);
    return this.http.get<User[]>(`${this.baseUrl}/search/name`, { params });
  }

  // Получить пользователей по статусу арендодателя
  getUsersByLessorStatus(isLessor: boolean): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/lessor/${isLessor}`);
  }
}