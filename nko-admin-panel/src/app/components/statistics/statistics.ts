import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StatisticsService } from '../../services/statistics.service';

// Material imports
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatListModule } from '@angular/material/list';

@Component({
  selector: 'app-statistics',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatIconModule,
    MatProgressBarModule,
    MatSlideToggleModule,
    MatButtonModule,
    MatTableModule,
    MatGridListModule,
    MatListModule
  ],
  templateUrl: './statistics.html',
  styleUrls: ['./statistics.scss']
})
export class StatisticsComponent implements OnInit {
  statistics: any = null;
  loading = false;
  error: string | null = null;
  includeAdvanced = false;

  // Колонки для таблиц
  categoryColumns: string[] = ['name', 'equipment', 'bookings'];
  itemColumns: string[] = ['name', 'bookings', 'quantity'];

  constructor(private statisticsService: StatisticsService) {}

  ngOnInit(): void {
    this.loadStatistics();
  }

  loadStatistics(): void {
    this.loading = true;
    this.error = null;

    this.statisticsService.getCompleteStatistics(this.includeAdvanced)
      .subscribe({
        next: (data) => {
          this.statistics = data;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Ошибка при загрузке статистики';
          this.loading = false;
          console.error('Error loading statistics:', error);
        }
      });
  }

  onIncludeAdvancedChange(): void {
    this.loadStatistics();
  }

  refreshStatistics(): void {
    this.loadStatistics();
  }
}