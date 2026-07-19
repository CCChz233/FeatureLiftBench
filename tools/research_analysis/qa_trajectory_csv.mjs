#!/usr/bin/env node
// Spreadsheet-layer QA for the generated trajectory CSV using artifact-tool.

import fs from "node:fs/promises";

const modulePath = process.env.ARTIFACT_TOOL_MODULE;
if (!modulePath) {
  throw new Error("Set ARTIFACT_TOOL_MODULE to artifact_tool.mjs");
}
const csvPath = process.argv[2] || "artifacts/research_analysis/trajectory_records.csv";
const { Workbook } = await import(modulePath);
const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText);
const sheet = workbook.worksheets.getFirst();
const used = sheet.getUsedRange();
const values = used ? used.values : [];
if (values.length === 0) {
  throw new Error("artifact-tool imported an empty worksheet");
}

const headers = values[0].map(String);
const required = [
  "task_id", "run_id", "model", "agent", "public_pass", "hidden_pass",
  "functional_pass", "extraction_ratio", "final_score", "copied_file_count",
  "copied_loc", "repeated_file_reads", "repeated_line_reads", "tool_error_count",
  "harness_format_error_count", "closure_plan_present", "self_generated_tests",
  "hidden_risk_discussed", "stop_reason", "primary_failure", "secondary_failure",
  "trajectory_path", "evaluation_path", "evidence_step_ids",
];
const missing = required.filter((name) => !headers.includes(name));
const formulaErrors = [];
const errorPattern = /#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A)/;
for (let row = 0; row < values.length; row += 1) {
  for (let col = 0; col < values[row].length; col += 1) {
    if (errorPattern.test(String(values[row][col] ?? ""))) {
      formulaErrors.push({ row: row + 1, col: col + 1, value: values[row][col] });
    }
  }
}

// Required by spreadsheet QA guidance.  The direct range read above is the
// authoritative check because CSV-import sheets in artifact-tool 2.8.22 do not
// expose their generated sheet id to the generic inspector consistently.
const inspectorErrorScan = workbook.inspect({
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100, matchFormulas: true },
});

const result = {
  csv_path: csvPath,
  worksheet: sheet.name,
  imported_rows_including_header: values.length,
  data_rows: values.length - 1,
  columns: headers.length,
  required_columns_missing: missing,
  duplicate_headers: headers.filter((name, index) => headers.indexOf(name) !== index),
  formula_error_cells: formulaErrors,
  inspector_error_scan: inspectorErrorScan,
  preview: {
    headers: headers.slice(0, 12),
    first_task_id: values[1]?.[headers.indexOf("task_id")] ?? null,
    last_task_id: values.at(-1)?.[headers.indexOf("task_id")] ?? null,
  },
};
console.log(JSON.stringify(result, null, 2));
if (missing.length || result.duplicate_headers.length || formulaErrors.length) {
  process.exitCode = 1;
}
