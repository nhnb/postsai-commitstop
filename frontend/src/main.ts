import { bootstrapApplication } from '@angular/platform-browser';
import { enableProdMode, provideZonelessChangeDetection, importProvidersFrom } from '@angular/core';
import { environment } from './environments/environment';

import { ConfigurationsService } from './app/configurations.service';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { AppComponent } from './app/app.component';
import { provideMonacoEditor } from 'ngx-monaco-editor-v2';

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, {
    providers: [
        importProvidersFrom(BrowserAnimationsModule, FormsModule, NgxDatatableModule),
        provideMonacoEditor(),
        ConfigurationsService, provideHttpClient(withInterceptorsFromDi())
    ]
});
