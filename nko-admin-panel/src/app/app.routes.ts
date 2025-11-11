import { Routes } from '@angular/router';

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
  { path: '**', redirectTo: '/users' }
];