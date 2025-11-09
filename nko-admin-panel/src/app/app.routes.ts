import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/users', pathMatch: 'full' },
  { 
    path: 'users', 
    loadComponent: () => import('./components/users/users').then(m => m.UsersComponent)
  },
  { path: '**', redirectTo: '/users' }
];