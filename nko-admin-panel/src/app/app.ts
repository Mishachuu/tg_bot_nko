import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    RouterOutlet,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  menuItems = [
    { title: 'Пользователи', route: '/users', icon: 'people' },
    // { title: 'Заявки', route: '/applications', icon: 'assignment' },
    // { title: 'Справочники', route: '/directories', icon: 'folder' }
  ];

  get currentTitle(): string {
    const currentRoute = window.location.pathname;
    const item = this.menuItems.find(menu => menu.route === currentRoute);
    return item ? item.title : 'NKO Admin';
  }
}