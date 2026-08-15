import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

import { ConfigurationsService } from './configurations.service';


import { AppComponent } from './app.component';
@NgModule( { declarations: [
        AppComponent
    ],
    bootstrap: [AppComponent], imports: [BrowserAnimationsModule,
        FormsModule,
        NgxDatatableModule], providers: [ConfigurationsService, provideHttpClient(withXhr(), withInterceptorsFromDi())] })
export class AppModule { }
