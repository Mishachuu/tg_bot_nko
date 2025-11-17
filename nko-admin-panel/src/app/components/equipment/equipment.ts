// equipment.component.ts (обновленная версия)
import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog } from '@angular/material/dialog';
import { Equipment, EquipmentService } from '../../services/equipment';
import { EquipmentPhotosDialogComponent, EquipmentPhotosDialogData } from '../equipment-photos-dialog/equipment-photos-dialog';

@Component({
  selector: 'app-equipment',
  templateUrl: './equipment.html',
  styleUrls: ['./equipment.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatMenuModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ]
})
export class EquipmentComponent implements OnInit {
  private equipmentService = inject(EquipmentService);
  private dialog = inject(MatDialog);
  currentEquipment: Equipment | null = null;
  displayedColumns: string[] = [
    'id', 'name', 'user_id', 'category_id', 'quantity', 
    'status', 'created_at', 'actions'
  ];
  
  dataSource = new MatTableDataSource<Equipment>([]);
  totalEquipment = signal(0);
  pageSize = 10;
  currentPage = 0;

  // Фильтры
  searchQuery = '';
  statusFilter = '';
  publishFilter = '';

  // Состояние загрузки
  isLoading = signal(false);

  ngOnInit() {
    this.loadEquipment();
  }

  setCurrentEquipment(equipment: Equipment): void {
    this.currentEquipment = equipment;
  }

  viewEquipmentPhotos(equipment: Equipment): void {
    this.dialog.open(EquipmentPhotosDialogComponent, {
      width: '900px',
      maxWidth: '95vw',
      data: {
        equipmentId: equipment.id,
        equipmentName: equipment.name
      } as EquipmentPhotosDialogData
    });
  }

  approveCurrentEquipment(): void {
    if (this.currentEquipment) {
      this.approveEquipment(this.currentEquipment);
    }
  }

  rejectCurrentEquipment(): void {
    if (this.currentEquipment) {
      this.rejectEquipment(this.currentEquipment);
    }
  }

  showRejectionReason(): void {
    if (this.currentEquipment?.rejection_reason) {
      alert(`Причина отклонения: ${this.currentEquipment.rejection_reason}`);
    } else {
      alert('Причина отклонения не указана');
    }
  }

  loadEquipment(): void {
    this.isLoading.set(true);
    
    this.equipmentService.getEquipment(this.currentPage * this.pageSize, this.pageSize)
      .subscribe({
        next: (response) => {
          this.dataSource.data = response.equipments;
          this.totalEquipment.set(response.total);
          this.isLoading.set(false);
        },
        error: (error) => {
          console.error('Error loading equipment:', error);
          this.isLoading.set(false);
        }
      });
  }

  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadEquipment();
  }

  // Методы для работы со статусами
  getStatusColor(status: string): string {
    switch (status) {
      case 'approved': return 'primary';
      case 'moderation': return 'warn';
      case 'rejected': return 'warn';
      default: return 'basic';
    }
  }

  getStatusDisplay(status: string): string {
    switch (status) {
      case 'approved': return '✅ Одобрено';
      case 'moderation': return '⏳ На модерации';
      case 'rejected': return '❌ Отклонено';
      default: return status;
    }
  }

  approveEquipment(equipment: Equipment): void {
    this.equipmentService.approveEquipment(equipment.id!)
      .subscribe({
        next: (updatedEquipment) => {
          equipment.status = updatedEquipment.status;
        },
        error: (error) => {
          console.error('Error approving equipment:', error);
        }
      });
  }

  rejectEquipment(equipment: Equipment): void {
    const reason = prompt('Введите причину отклонения:');
    if (reason !== null) {
      this.equipmentService.rejectEquipment(equipment.id!, reason)
        .subscribe({
          next: (updatedEquipment) => {
            equipment.status = updatedEquipment.status;
            equipment.rejection_reason = updatedEquipment.rejection_reason;
          },
          error: (error) => {
            console.error('Error rejecting equipment:', error);
          }
        });
    }
  }
}