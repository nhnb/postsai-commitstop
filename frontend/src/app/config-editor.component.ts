import { Component, model } from "@angular/core";
import { EditorComponent } from "ngx-monaco-editor-v2";
import { FormsModule } from "@angular/forms";

@Component({
  selector: "app-config-editor",
  templateUrl: "./config-editor.component.html",
  imports: [EditorComponent, FormsModule],
})
export class ConfigEditorComponent {
  code = model();

  editorOptions = {
    theme: "vs",
    language: "myCustomConfig",
    automaticLayout: true,
    fontSize: 14,
    minimap: { enabled: false },
  };

  onEditorInit(editor: any) {
    // The 'monaco' object is globally available on the window
    // once the ngx-monaco-editor has loaded its assets.
    const monaco = (window as any).monaco;

    if (!monaco) {
      console.error("Monaco is not loaded yet");
      return;
    }

    // 1. Register the custom language
    monaco.languages.register({ id: "myCustomConfig" });

    // 2. Set the tokens (from the ConfigLanguageDefinition provided in previous response)
    monaco.languages.setMonarchTokensProvider("myCustomConfig", {
      tokenizer: {
        root: [
          [/^#.*$/, "comment"],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, "invalid"],
          [/\s+/, "white"],
        ],
        col1: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, { token: "col1", next: "@col2" }],
          [/\s+/, "white"],
        ],
        col2: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, { token: "col2", next: "@col3" }],
          [/\s+/, "white"],
        ],
        col3: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, { token: "col3", next: "@col4" }],
          [/\s+/, "white"],
        ],
        col4: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, { token: "col4", next: "@col5" }],
          [/\s+/, "white"],
        ],
        col5: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\S+/, { token: "col5", next: "@message" }],
          [/\s+/, "white"],
        ],
        message: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@col1" }],
          [/\s+/, "white"],
          [/.+$/, { token: "message", next: "@root" }],
        ],
      },
    });

    // 3. Set the Theme
    monaco.editor.defineTheme("vs", {
      base: "vs",
      inherit: true,
      rules: [
        { token: "comment", foreground: "6A9955", fontStyle: "italic" },
        { token: "operator", foreground: "FF8000", fontWeight: "bold" },
        { token: "col1", foreground: "0451A5" },
        { token: "col2", foreground: "098658" },
        { token: "col3", foreground: "AF00DB" },
        { token: "col4", foreground: "A31515" },
        { token: "col5", foreground: "001080" },
        { token: "message", foreground: "808080", fontStyle: "italic" },
      ],
      colors: {},
    });

    // 4. Syntax Validation Logic
    editor.onDidChangeModelContent(() => {
      this.validateConfig(editor);
    });

    this.validateConfig(editor);
  }

  validateConfig(editor: any) {
    const monaco = (window as any).monaco;
    const model = editor.getModel();
    const content = model.getValue();
    const lines = content.split("\n");
    const markers: any[] = [];

    lines.forEach((lineText: string, index: number) => {
      const trimmed = lineText.trim();
      if (!trimmed || trimmed.startsWith("#")) {
        return;
      }

      if (!trimmed.startsWith("+") && !trimmed.startsWith("-")) {
        markers.push(
          this.createMarker(
            index,
            1,
            lineText.length,
            "Line must start with + or - or #.",
          ),
        );
        return;
      }

      const contentWithoutOp = trimmed.substring(1).trim();
      const parts = contentWithoutOp.split(/\s+/);

      if (parts.length < 5) {
        markers.push(
          this.createMarker(
            index,
            1,
            lineText.length,
            `Missing columns: expected 5 regex columns, found ${parts.length}`,
          ),
        );
      } else {
        let searchFrom = lineText.indexOf(trimmed[0]) + 1;
        for (let i = 0; i < 5; i++) {
          const partPos = lineText.indexOf(parts[i], searchFrom);
          if (!this.isValidRegex(parts[i])) {
            markers.push(
              this.createMarker(
                index,
                partPos + 1,
                parts[i].length,
                `Invalid Regular Expression: ${parts[i]}`,
              ),
            );
          }
          searchFrom = partPos + parts[i].length;
        }
      }
    });

    monaco.editor.setModelMarkers(model, "owner", markers);
  }

  private isValidRegex(str: string): boolean {
    try {
      new RegExp(str);
      return true;
    } catch (e) {
      return false;
    }
  }

  private createMarker(
    line: number,
    startCol: number,
    length: number,
    message: string,
  ) {
    return {
      startLineNumber: line + 1,
      startColumn: startCol,
      endLineNumber: line + 1,
      endColumn: startCol + length,
      message: message,
      severity: 8, // Error
    };
  }
}
