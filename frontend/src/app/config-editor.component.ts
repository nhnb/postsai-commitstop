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
  private decorationIds: string[] = [];

  editorOptions = {
    theme: "vs",
    language: "myCustomConfig",
    automaticLayout: true,
    fontSize: 14,
    minimap: { enabled: false },
    glyphMargin: true,
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
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, "invalid"],
          [/\s+/, "white"],
        ],
        repository: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, { token: "repository", next: "@branch" }],
          [/\s+/, "white"],
        ],
        branch: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, { token: "branch", next: "@user" }],
          [/\s+/, "white"],
        ],
        user: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, { token: "user", next: "@group" }],
          [/\s+/, "white"],
        ],
        group: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, { token: "group", next: "@commitmessage" }],
          [/\s+/, "white"],
        ],
        commitmessage: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
          [/\S+/, { token: "commitmessage", next: "@message" }],
          [/\s+/, "white"],
        ],
        message: [
          [/^#.*$/, { token: "comment", next: "@root" }],
          [/^[\+\-]/, { token: "operator", next: "@repository" }],
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
        { token: "repository", foreground: "0451A5" },
        { token: "branch", foreground: "098658" },
        { token: "user", foreground: "AF00DB" },
        { token: "group", foreground: "A31515" },
        { token: "commitmessage", foreground: "001080" },
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

    const decorations = markers.map((m: any) => ({
      range: new monaco.Range(
        m.startLineNumber,
        m.startColumn,
        m.endLineNumber,
        m.endColumn,
      ),
      options: { glyphMarginClassName: "error-glyph" },
    }));
    this.decorationIds = editor.deltaDecorations(
      this.decorationIds || [],
      decorations,
    );
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
