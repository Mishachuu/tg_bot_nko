import { Component, OnInit, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';

import { UserService, User } from '../../services/user';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatMenuModule
  ],
  templateUrl: './users.html',
  styleUrl: './users.scss'
})
export class UsersComponent implements OnInit {
  displayedColumns: string[] = ['id', 'name', 'tg_id', 'email', 'phone_number', 'score', 'is_lessor', 'actions'];
  dataSource = new MatTableDataSource<User>();
  
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  isLoading = signal(false);
  totalUsers = signal(0);
  pageSize = 10;
  currentPage = 0;
  searchQuery = '';
  lessorFilter = '';

  constructor(
    private userService: UserService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadUsers();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadUsers() {
    this.isLoading.set(true);
    const skip = this.currentPage * this.pageSize;

    this.userService.getUsers(skip, this.pageSize).subscribe({
      next: (response) => {
        this.dataSource.data = response.users;
        this.totalUsers.set(response.total);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.isLoading.set(false);
        this.showError('Ошибка загрузки пользователей');
      }
    });
  }

  onSearch() {
    if (this.searchQuery.length >= 2) {
      this.userService.searchUsersByName(this.searchQuery).subscribe({
        next: (users) => {
          this.dataSource.data = users;
          this.totalUsers.set(users.length);
        },
        error: (error) => {
          console.error('Error searching users:', error);
          this.showError('Ошибка поиска');
        }
      });
    } else if (this.searchQuery.length === 0) {
      this.loadUsers();
    }
  }

  onPageChange(event: any) {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadUsers();
  }

  toggleLessorStatus(user: User) {
    const newStatus = !user.is_lessor;
    this.userService.updateLessorStatus(user.id!, newStatus).subscribe({
      next: (updatedUser) => {
        user.is_lessor = updatedUser.is_lessor;
        this.showSuccess(`Статус пользователя обновлен`);
      },
      error: (error) => {
        console.error('Error updating lessor status:', error);
        this.showError('Ошибка обновления статуса');
      }
    });
  }

  editUser(user: User) {
    // TODO: Реализовать диалог редактирования
    this.showSuccess(`Редактирование пользователя ${user.name}`);
  }

  deleteUser(userId: number) {
    if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
      this.userService.deleteUser(userId).subscribe({
        next: () => {
          this.loadUsers();
          this.showSuccess('Пользователь удален');
        },
        error: (error) => {
          console.error('Error deleting user:', error);
          this.showError('Ошибка удаления пользователя');
        }
      });
    }
  }

  private showSuccess(message: string) {
    this.snackBar.open(message, 'Закрыть', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string) {
    this.snackBar.open(message, 'Закрыть', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}