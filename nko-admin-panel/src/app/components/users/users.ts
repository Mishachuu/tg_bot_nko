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

    let isLessor: boolean | undefined;
    if (this.lessorFilter === 'true') {
      isLessor = true;
    } else if (this.lessorFilter === 'false') {
      isLessor = false;
    }

    this.userService.getUsers(skip, this.pageSize, isLessor).subscribe({
      next: (response) => {
        this.dataSource.data = response.users;
        this.totalUsers.set(response.total);
        this.isLoading.set(false);
        this.updatePaginator();
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.isLoading.set(false);
        this.showError('Ошибка загрузки пользователей');
      }
    });
  }

  onFilterChange() {
    this.currentPage = 0;
    this.loadUsers();
  }

  onSearch() {
    if (this.searchQuery.length >= 2) {
      this.userService.searchUsersByName(this.searchQuery).subscribe({
        next: (users) => {
          this.dataSource.data = users;
          this.totalUsers.set(users.length);
          this.currentPage = 0;
          this.updatePaginator();
        },
        error: (error) => {
          console.error('Error searching users:', error);
          this.showError('Ошибка поиска');
        }
      });
    } else if (this.searchQuery.length === 0) {
      this.currentPage = 0;
      this.loadUsers();
    }
  }

  onPageChange(event: any) {
    if (event.pageSize !== this.pageSize) {
      this.currentPage = 0;
    } else {
      this.currentPage = event.pageIndex;
    }
    this.pageSize = event.pageSize;
    this.loadUsers();
  }

  // НОВЫЕ МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ СТАТУСОМ АРЕНДОДАТЕЛЯ
  grantLessorStatus(user: User) {
    if (confirm(`Назначить пользователя "${user.name}" арендодателем?`)) {
      this.userService.updateLessorStatus(user.id!, true).subscribe({
        next: (updatedUser) => {
          user.is_lessor = updatedUser.is_lessor;
          this.showSuccess(`Пользователь "${user.name}" назначен арендодателем`);
          this.loadUsers(); // Перезагружаем для обновления данных
        },
        error: (error) => {
          console.error('Error granting lessor status:', error);
          this.showError('Ошибка назначения статуса арендодателя');
        }
      });
    }
  }

  revokeLessorStatus(user: User) {
    if (confirm(`Отозвать права арендодателя у пользователя "${user.name}"?`)) {
      this.userService.updateLessorStatus(user.id!, false).subscribe({
        next: (updatedUser) => {
          user.is_lessor = updatedUser.is_lessor;
          this.showSuccess(`Права арендодателя отозваны у пользователя "${user.name}"`);
          this.loadUsers(); // Перезагружаем для обновления данных
        },
        error: (error) => {
          console.error('Error revoking lessor status:', error);
          this.showError('Ошибка отзыва статуса арендодателя');
        }
      });
    }
  }

  // УДАЛЕН МЕТОД toggleLessorStatus - больше не нужен

  private updatePaginator() {
    if (this.paginator) {
      const totalPages = Math.ceil(this.totalUsers() / this.pageSize);
      if (this.currentPage >= totalPages && totalPages > 0) {
        this.currentPage = totalPages - 1;
        this.loadUsers();
        return;
      }
      
      setTimeout(() => {
        this.paginator.pageIndex = this.currentPage;
        this.paginator.length = this.totalUsers();
      });
    }
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