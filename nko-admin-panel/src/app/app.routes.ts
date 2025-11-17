import { Routes } from '@angular/router';
import { StatisticsComponent } from './components/statistics/statistics';

export const routes: Routes = [
  { path: '', redirectTo: '/users', pathMatch: 'full' },
  { 
    path: 'users', 
    loadComponent: () => import('./components/users/users').then(m => m.UsersComponent)
  },
  { 
    path: 'equipment', 
    loadComponent: () => import('./components/equipment/equipment').then(m => m.EquipmentComponent)
  },
  { 
    path: 'statistics', 
    loadComponent: () => import('./components/statistics/statistics').then(m => m.StatisticsComponent)
  },
  { path: '**', redirectTo: '/users' }
];