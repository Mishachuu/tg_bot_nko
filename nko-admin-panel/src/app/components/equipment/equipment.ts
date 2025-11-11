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

import { EquipmentService, Equipment, EquipmentSearchParams } from '../../services/equipment';

@Component({
  selector: 'app-equipment',
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
  templateUrl: './equipment.html',
  styleUrl: './equipment.scss'
})
export class EquipmentComponent implements OnInit {
  displayedColumns: string[] = [
    'id', 
    'name', 
    'user_id', 
    'category_id', 
    'quantity', 
    'is_approved', 
    'is_publish', 
    'created_at', 
    'actions'
  ];
  dataSource = new MatTableDataSource<Equipment>();
  
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  isLoading = signal(false);
  totalEquipment = signal(0);
  pageSize = 10;
  currentPage = 0;
  searchQuery = '';
  approvalFilter = '';
  publishFilter = '';

  constructor(
    private equipmentService: EquipmentService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadEquipment();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadEquipment() {
    this.isLoading.set(true);
    const skip = this.currentPage * this.pageSize;

    this.equipmentService.getEquipment(skip, this.pageSize).subscribe({
      next: (response) => {
        this.dataSource.data = response.equipments;
        this.totalEquipment.set(response.total);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading equipment:', error);
        this.isLoading.set(false);
        this.showError('Ошибка загрузки оборудования');
      }
    });
  }

  onSearch() {
    if (this.searchQuery.length >= 2) {
      const searchParams: EquipmentSearchParams = {
        name: this.searchQuery
      };
      
      this.equipmentService.searchEquipment(searchParams).subscribe({
        next: (equipments) => {
          this.dataSource.data = equipments;
          this.totalEquipment.set(equipments.length);
        },
        error: (error) => {
          console.error('Error searching equipment:', error);
          this.showError('Ошибка поиска');
        }
      });
    } else if (this.searchQuery.length === 0) {
      this.loadEquipment();
    }
  }

  onPageChange(event: any) {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadEquipment();
  }

  toggleApprovalStatus(equipment: Equipment) {
    const newStatus = !equipment.is_approved;
    this.equipmentService.updateApprovalStatus(equipment.id!, newStatus).subscribe({
      next: (updatedEquipment) => {
        equipment.is_approved = updatedEquipment.is_approved;
        this.showSuccess(`Статус одобрения обновлен`);
      },
      error: (error) => {
        console.error('Error updating approval status:', error);
        this.showError('Ошибка обновления статуса одобрения');
      }
    });
  }

  togglePublishStatus(equipment: Equipment) {
    const newStatus = !equipment.is_publish;
    this.equipmentService.updatePublishStatus(equipment.id!, newStatus).subscribe({
      next: (updatedEquipment) => {
        equipment.is_publish = updatedEquipment.is_publish;
        this.showSuccess(`Статус публикации обновлен`);
      },
      error: (error) => {
        console.error('Error updating publish status:', error);
        this.showError('Ошибка обновления статуса публикации');
      }
    });
  }

  editEquipment(equipment: Equipment) {
    // TODO: Реализовать диалог редактирования
    this.showSuccess(`Редактирование оборудования "${equipment.name}"`);
  }

  viewEquipmentDetails(equipment: Equipment) {
    // TODO: Реализовать просмотр деталей
    this.showSuccess(`Просмотр оборудования "${equipment.name}"`);
  }

  deleteEquipment(equipmentId: number) {
    if (confirm('Вы уверены, что хотите удалить это оборудование?')) {
      this.equipmentService.deleteEquipment(equipmentId).subscribe({
        next: () => {
          this.loadEquipment();
          this.showSuccess('Оборудование удалено');
        },
        error: (error) => {
          console.error('Error deleting equipment:', error);
          this.showError('Ошибка удаления оборудования');
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