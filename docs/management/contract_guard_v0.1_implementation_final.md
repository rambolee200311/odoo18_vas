# Contract Guard v0.1 — 实施交付稿

> 状态：架构冻结；实现待验证。保留原实施手册，供 Codex 落地使用。文中的 PASS、READY 均为预期验收条件，不代表已经运行测试。

## 本轮收口

不再扩展架构。先完成以下实现验收，再接入 Warehouse VAS CC-01：

1. **基线与信任**：使用 Human 批准的完整 Execution Baseline SHA；Preflight 校验 HEAD 一致。Guard 与 Policy 必须来自批准基线，不能仅凭 Agent 自行选择的 HEAD 建立信任。
2. **Git fail-closed**：修正 raw diff 解析，覆盖 staged、unstaged、untracked、删除、重命名、类型变化及异常状态；Git 错误不得返回 PASS。Boundary 校验 Policy schema，并拒绝未授权 HEAD 漂移。
3. **测试隔离**：Guard 自身测试只使用独立临时仓库和 mock runner；不得依赖真实 Odoo 数据库不存在来制造失败。必须证明测试前 Boundary PASS、测试执行后产生越界文件、测试后 Boundary FAIL。
4. **测试证据**：CLOSE 保留实际命令、退出码和测试输出；退出码 0 不自动等于必需测试已执行。
5. **Evidence**：在基线前提交 `.guard/evidence/` 的 ignore 规则；记录基线、Policy fingerprint、实际代码状态和测试结果。Evidence 是可复核记录，不是不可伪造证明。
6. **异常与权限**：Guard 内部异常必须非零退出；不得修改 Guard、CC、测试配置或清理真实工作区来绕过失败。数据库连接与隔离由批准的测试环境负责，Guard 不承担数据库治理。

**验收门槛**：Guard 自身正向及负向测试全部通过 → Human/CI 在可信环境复核 → 才允许执行 VAS CC-01。未运行的测试不得标记 PASS。

---

你的评审完全正确。这些问题都是实现层面的收口，不是架构问题。我现在直接给出修正后的完整代码和测试。

---

# Contract Guard v0.1 最终实施手册

## 冻结的架构（不再讨论）

```text
Execution Baseline = 包含 Approved CC + Guard + 开工代码状态的 commit

PRE-FLIGHT:
  HEAD == execution_baseline
  + worktree clean
  + CC approved
  + schema valid
  → PASS / BLOCK

BOUNDARY:
  execution_baseline → current worktree Git delta
  + allowlist
  + protected
  → PASS / BLOCK

CLOSE:
  boundary
  → mandatory tests
  → boundary again
  → evidence
  → PASS / BLOCK
```

**数据库定位**：Guard 只执行 CC 中已批准的测试数据库参数，不承担数据库治理。

---

## 一、修正内容

| # | 问题 | 修正 |
|---|---|---|
| P0-1 | Preflight 缺少 `HEAD == baseline` | 增加检查，不等则 BLOCK |
| P0-2 | Shell 测试脚本无法跑完 | 改为 Python 单元测试，负向测试用 assert |
| P0-3 | Evidence 污染下次检查 | 在建立 Execution Baseline 前将 `.guard/evidence/` 加入 `.gitignore` |
| P1-1 | Baseline 定义不统一 | 统一为 `Execution Baseline`，CLI 参数仍为 `--baseline` |
| P1-2 | Schema 验证不完整 | 增加必填字段和类型检查 |

---

## 二、修正后的完整代码

**文件：`.guard/contract_guard.py`**

```python
#!/usr/bin/env python3
"""
Contract Guard v0.1 - Workflow / CC Compliance Checker

Execution Baseline = Human 批准本轮执行后形成的 Git commit，
其中已经包含 Approved CC、Guard 版本以及本轮 Agent 开工前的仓库状态。

使用方式:
    python .guard/contract_guard.py preflight --cc-path <CC文件> --baseline <Execution Baseline>
    python .guard/contract_guard.py boundary --cc-path <CC文件> --baseline <Execution Baseline>
    python .guard/contract_guard.py close --cc-path <CC文件> --baseline <Execution Baseline>
"""

import sys
import json
import subprocess
import yaml
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class ContractGuardError(Exception):
    """Guard 内部错误 - 必须 FAIL，不能 PASS"""
    pass


class ContractGuard:
    def __init__(self, cc_path: str, baseline: str):
        self.cc_path = cc_path
        self.baseline = baseline  # Execution Baseline
        self.guard_version = "0.1.0"
        self._policy = None
        self._repo_root = self._find_repo_root()
        self._evidence_dir = self._repo_root / ".guard" / "evidence"

    # ========== Repository Utilities ==========

    def _find_repo_root(self) -> Path:
        try:
            result = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                text=True
            ).strip()
            return Path(result)
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Not in a git repository: {e}")

    def _get_current_head(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                text=True
            ).strip()
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Failed to get HEAD: {e}")

    def _resolve_baseline(self) -> str:
        """解析 Execution Baseline 的完整 SHA"""
        try:
            return subprocess.check_output(
                ["git", "rev-parse", self.baseline],
                text=True
            ).strip()
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Failed to resolve baseline '{self.baseline}': {e}")

    def _is_worktree_clean(self) -> Tuple[bool, List[str]]:
        try:
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                text=True
            ).strip()
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Failed to get git status: {e}")

        if status:
            return False, status.split('\n')
        return True, []

    # ========== Policy Loading ==========

    def _load_policy_from_baseline(self) -> dict:
        """从 Execution Baseline 读取 CC 中的 Enforcement Block"""
        try:
            content = subprocess.check_output(
                ["git", "show", f"{self.baseline}:{self.cc_path}"],
                text=True,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(
                f"Failed to read CC from baseline {self.baseline}: {self.cc_path} not tracked. {e}"
            )

        start_marker = "<!-- CONTRACT_ENFORCEMENT_START -->"
        end_marker = "<!-- CONTRACT_ENFORCEMENT_END -->"

        if start_marker not in content or end_marker not in content:
            raise ContractGuardError(
                f"Enforcement block markers not found in CC: {self.cc_path}"
            )

        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker)
        yaml_content = content[start_idx:end_idx].strip()

        if yaml_content.startswith("```yaml"):
            yaml_content = yaml_content[7:]
        if yaml_content.endswith("```"):
            yaml_content = yaml_content[:-3]

        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ContractGuardError(f"Invalid YAML in enforcement block: {e}")

        enforcement = data.get('enforcement', {})
        if not enforcement:
            raise ContractGuardError("No 'enforcement' key found in YAML")

        return enforcement

    def _get_policy(self) -> dict:
        if self._policy is None:
            self._policy = self._load_policy_from_baseline()
        return self._policy

    def _get_policy_fingerprint(self) -> str:
        """计算完整 policy 的 fingerprint"""
        policy = self._get_policy()
        content = json.dumps(policy, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _validate_schema(self, policy: dict) -> List[dict]:
        """验证 Policy schema，返回 checks"""
        checks = []
        overall = "PASS"

        # 必填字段
        required_fields = {
            "schema_version": str,
            "contract_id": str,
            "status": str,
            "allowed_modify": list,
            "allowed_create": list,
            "allowed_delete": list,
            "protected": list,
        }

        for field, field_type in required_fields.items():
            if field not in policy:
                checks.append({
                    "name": f"SCHEMA_{field.upper()}",
                    "status": "FAIL",
                    "message": f"Missing required field: {field}"
                })
                overall = "FAIL"
                continue

            if not isinstance(policy[field], field_type):
                checks.append({
                    "name": f"SCHEMA_{field.upper()}",
                    "status": "FAIL",
                    "message": f"Field {field} must be {field_type.__name__}, got {type(policy[field]).__name__}"
                })
                overall = "FAIL"
                continue

            # 对 list 类型检查元素是否为字符串
            if field_type == list:
                for item in policy[field]:
                    if not isinstance(item, str):
                        checks.append({
                            "name": f"SCHEMA_{field.upper()}",
                            "status": "FAIL",
                            "message": f"Field {field} must contain strings only"
                        })
                        overall = "FAIL"
                        break

        # 检查 tests.database 和 tests.module
        tests = policy.get("tests", {})
        if not isinstance(tests, dict):
            checks.append({
                "name": "SCHEMA_TESTS",
                "status": "FAIL",
                "message": "tests must be a dict"
            })
            overall = "FAIL"
        else:
            if "database" not in tests:
                checks.append({
                    "name": "SCHEMA_TESTS_DATABASE",
                    "status": "FAIL",
                    "message": "tests.database is required"
                })
                overall = "FAIL"
            elif not isinstance(tests["database"], str):
                checks.append({
                    "name": "SCHEMA_TESTS_DATABASE",
                    "status": "FAIL",
                    "message": "tests.database must be a string"
                })
                overall = "FAIL"
            else:
                checks.append({
                    "name": "SCHEMA_TESTS_DATABASE",
                    "status": "PASS",
                    "database": tests["database"]
                })

            if "module" not in tests:
                checks.append({
                    "name": "SCHEMA_TESTS_MODULE",
                    "status": "FAIL",
                    "message": "tests.module is required"
                })
                overall = "FAIL"
            elif not isinstance(tests["module"], str):
                checks.append({
                    "name": "SCHEMA_TESTS_MODULE",
                    "status": "FAIL",
                    "message": "tests.module must be a string"
                })
                overall = "FAIL"
            else:
                checks.append({
                    "name": "SCHEMA_TESTS_MODULE",
                    "status": "PASS",
                    "module": tests["module"]
                })

        # 添加整体 schema 检查结果
        if overall == "PASS":
            checks.insert(0, {"name": "SCHEMA", "status": "PASS"})
        else:
            checks.insert(0, {"name": "SCHEMA", "status": "FAIL", "message": "Schema validation failed"})

        return checks

    # ========== Git Delta 分析 (Fail-Closed) ==========

    def _parse_raw_diff(self, raw_output: str) -> dict:
        """
        解析 git diff --raw -z 输出
        格式: :<old-mode> <new-mode> <old-sha> <new-sha> <status> [<old-file>\0<new-file>\0]
        状态: M=modified, A=added, D=deleted, R=renamed, T=type-change
        """
        result = {
            "modified": [],
            "created": [],
            "deleted": [],
            "renamed": [],
            "type_changed": []
        }

        if not raw_output:
            return result

        parts = [p for p in raw_output.split('\0') if p]
        i = 0

        while i < len(parts):
            entry = parts[i]
            if not entry.startswith(':'):
                i += 1
                continue

            fields = entry.split()
            if len(fields) < 5:
                raise ContractGuardError(f"Malformed raw diff entry: {entry}")

            status_code = fields[4]
            status_char = status_code[0] if status_code else '?'

            if status_char == 'M':
                i += 1
                if i >= len(parts):
                    raise ContractGuardError("Raw diff: missing file path for modified")
                result["modified"].append(parts[i])
                i += 1

            elif status_char == 'A':
                i += 1
                if i >= len(parts):
                    raise ContractGuardError("Raw diff: missing file path for added")
                result["created"].append(parts[i])
                i += 1

            elif status_char == 'D':
                i += 1
                if i >= len(parts):
                    raise ContractGuardError("Raw diff: missing file path for deleted")
                result["deleted"].append(parts[i])
                i += 1

            elif status_char == 'R':
                i += 1
                if i + 1 >= len(parts):
                    raise ContractGuardError("Raw diff: missing rename paths")
                result["renamed"].append({"from": parts[i], "to": parts[i + 1]})
                i += 2

            elif status_char == 'T':
                i += 1
                if i >= len(parts):
                    raise ContractGuardError("Raw diff: missing file path for type-change")
                result["type_changed"].append(parts[i])
                i += 1

            else:
                raise ContractGuardError(f"Unknown status code in raw diff: {status_char}")

        return result

    def _get_working_tree_delta(self) -> dict:
        """获取相对于 Execution Baseline 的完整工作区变更"""
        result = {
            "changed_files": [],
            "modified": [],
            "created": [],
            "deleted": [],
            "renamed": [],
            "type_changed": []
        }

        # 1. Tracked changes
        try:
            raw_output = subprocess.check_output(
                ["git", "diff", "--raw", "-z", self.baseline],
                text=True
            ).strip('\0')
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Failed to get git diff: {e}")

        parsed = self._parse_raw_diff(raw_output)
        for key in ["modified", "created", "deleted", "renamed", "type_changed"]:
            result[key] = parsed.get(key, [])

        # 2. Untracked files (排除 .gitignore 中的内容)
        try:
            untracked = subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard", "-z"],
                text=True
            ).strip('\0')
            if untracked:
                result["created"].extend([f for f in untracked.split('\0') if f])
        except subprocess.CalledProcessError as e:
            raise ContractGuardError(f"Failed to get untracked files: {e}")

        # 3. 汇总
        changed = set()
        changed.update(result["modified"])
        changed.update(result["created"])
        changed.update(result["deleted"])
        for rename in result["renamed"]:
            changed.add(rename["to"])
        changed.update(result["type_changed"])
        result["changed_files"] = list(changed)

        return result

    # ========== Boundary Check ==========

    def _is_allowed(self, file_path: str, change_type: str) -> bool:
        policy = self._get_policy()
        if change_type == "modified":
            allowlist = policy.get("allowed_modify", [])
        elif change_type == "created":
            allowlist = policy.get("allowed_create", [])
        elif change_type == "deleted":
            allowlist = policy.get("allowed_delete", [])
        else:
            return False
        return file_path in allowlist

    def _is_protected(self, file_path: str) -> bool:
        policy = self._get_policy()
        import fnmatch
        for pattern in policy.get("protected", []):
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def check_boundary(self) -> dict:
        """边界检查：当前工作区是否在授权范围内"""
        try:
            policy = self._get_policy()
        except ContractGuardError as e:
            return {"overall": "FAIL", "message": f"Policy load failed: {e}"}

        try:
            delta = self._get_working_tree_delta()
        except ContractGuardError as e:
            return {"overall": "FAIL", "message": f"Git delta failed: {e}"}

        if not delta["changed_files"]:
            return {
                "overall": "PASS",
                "message": "No changes",
                "changed_files": [],
                "policy_fingerprint": self._get_policy_fingerprint()
            }

        violations = []

        for file_path in delta["modified"]:
            if self._is_protected(file_path):
                violations.append({"file": file_path, "reason": "PROTECTED_MODIFY"})
            elif not self._is_allowed(file_path, "modified"):
                violations.append({"file": file_path, "reason": "UNAUTHORIZED_MODIFY"})

        for file_path in delta["created"]:
            if self._is_protected(file_path):
                violations.append({"file": file_path, "reason": "PROTECTED_CREATE"})
            elif not self._is_allowed(file_path, "created"):
                violations.append({"file": file_path, "reason": "UNAUTHORIZED_CREATE"})

        for file_path in delta["deleted"]:
            if self._is_protected(file_path):
                violations.append({"file": file_path, "reason": "PROTECTED_DELETE"})
            elif not self._is_allowed(file_path, "deleted"):
                violations.append({"file": file_path, "reason": "UNAUTHORIZED_DELETE"})

        for rename in delta["renamed"]:
            violations.append({
                "file": f"{rename['from']} → {rename['to']}",
                "reason": "RENAME_NOT_ALLOWED"
            })

        for file_path in delta["type_changed"]:
            violations.append({
                "file": file_path,
                "reason": "TYPE_CHANGE_NOT_ALLOWED"
            })

        if violations:
            return {
                "overall": "FAIL",
                "violations": violations,
                "summary": f"{len(violations)} violations found",
                "changed_files": delta["changed_files"],
                "policy_fingerprint": self._get_policy_fingerprint()
            }

        return {
            "overall": "PASS",
            "changed_files": delta["changed_files"],
            "summary": f"All {len(delta['changed_files'])} changes are authorized",
            "policy_fingerprint": self._get_policy_fingerprint()
        }

    # ========== Test Execution ==========

    def _build_test_command(self) -> List[str]:
        policy = self._get_policy()
        tests = policy.get("tests", {})
        runner = tests.get("runner", {})

        cmd = [
            runner.get("python", "python3"),
            runner.get("odoo_bin", "odoo-bin"),
            "--config", tests.get("odoo_config", "odoo.conf"),
            "--database", tests["database"],
            "--addons-path", ",".join(tests.get("addons_path", ["addons"])),
            "--test-enable",
            "--stop-after-init",
            "-u", tests["module"],
            "--log-level", "error"
        ]

        if tests.get("test_tags"):
            cmd.extend(["--test-tags", ",".join(tests["test_tags"])])

        return cmd

    def run_tests(self) -> dict:
        try:
            policy = self._get_policy()
        except ContractGuardError as e:
            return {"overall": "FAIL", "message": f"Policy load failed: {e}"}

        tests = policy.get("tests", {})
        if not tests.get("database") or not tests.get("module"):
            return {"overall": "FAIL", "message": "Missing database or module in test config"}

        try:
            cmd = self._build_test_command()
        except ContractGuardError as e:
            return {"overall": "FAIL", "message": str(e)}

        timeout = tests.get("timeout_seconds", 300)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self._repo_root)
            )
            return {
                "overall": "PASS" if result.returncode == 0 else "FAIL",
                "exit_code": result.returncode,
                "database": tests["database"],
                "command": " ".join(cmd),
                "stdout_tail": result.stdout[-500:] if result.stdout else "",
                "stderr_tail": result.stderr[-500:] if result.stderr else "",
                "policy_fingerprint": self._get_policy_fingerprint()
            }
        except subprocess.TimeoutExpired:
            return {"overall": "FAIL", "message": f"Test timeout after {timeout}s"}
        except FileNotFoundError as e:
            return {"overall": "FAIL", "message": f"Command not found: {e}"}

    # ========== Evidence ==========

    def _save_evidence(self, result: dict) -> Path:
        self._evidence_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        contract_id = self._get_policy().get("contract_id", "unknown")
        filename = f"{timestamp}_{contract_id}_evidence.json"
        filepath = self._evidence_dir / filename

        evidence = {
            "evidence_version": "0.1",
            "guard_version": self.guard_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "baseline": self._resolve_baseline(),
            "cc_path": self.cc_path,
            "head": self._get_current_head(),
            "policy_fingerprint": self._get_policy_fingerprint(),
            "result": result
        }

        with open(filepath, 'w') as f:
            json.dump(evidence, f, indent=2)

        return filepath

    # ========== Three Gates ==========

    def preflight(self) -> dict:
        """PRE-FLIGHT: HEAD == baseline + worktree clean + CC approved + schema valid"""
        checks = []
        overall = "PASS"

        # 1. HEAD == Execution Baseline
        try:
            baseline_sha = self._resolve_baseline()
            current_head = self._get_current_head()

            if current_head != baseline_sha:
                checks.append({
                    "name": "EXECUTION_BASELINE",
                    "status": "FAIL",
                    "expected": baseline_sha,
                    "actual": current_head,
                    "message": "HEAD does not match Execution Baseline"
                })
                overall = "FAIL"
            else:
                checks.append({
                    "name": "EXECUTION_BASELINE",
                    "status": "PASS",
                    "sha": baseline_sha
                })
        except ContractGuardError as e:
            checks.append({"name": "EXECUTION_BASELINE", "status": "FAIL", "message": str(e)})
            overall = "FAIL"

        # 2. 从 baseline 读取 Policy
        try:
            policy = self._get_policy()
            checks.append({"name": "POLICY_LOAD", "status": "PASS"})
        except ContractGuardError as e:
            checks.append({"name": "POLICY_LOAD", "status": "FAIL", "message": str(e)})
            overall = "FAIL"
            return {
                "contract_id": "unknown",
                "guard_version": self.guard_version,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": checks,
                "overall": overall
            }

        # 3. CC status
        if policy.get("status") != "approved":
            checks.append({
                "name": "CC_STATUS",
                "status": "FAIL",
                "message": f"CC status is '{policy.get('status')}', expected 'approved'"
            })
            overall = "FAIL"
        else:
            checks.append({"name": "CC_STATUS", "status": "PASS"})

        # 4. Worktree clean
        try:
            is_clean, changes = self._is_worktree_clean()
            if not is_clean:
                checks.append({
                    "name": "WORKTREE_CLEAN",
                    "status": "FAIL",
                    "changes": changes[:10],
                    "message": f"Working tree has {len(changes)} uncommitted changes"
                })
                overall = "FAIL"
            else:
                checks.append({"name": "WORKTREE_CLEAN", "status": "PASS"})
        except ContractGuardError as e:
            checks.append({"name": "WORKTREE_CLEAN", "status": "FAIL", "message": str(e)})
            overall = "FAIL"

        # 5. Schema validation
        schema_checks = self._validate_schema(policy)
        for check in schema_checks:
            checks.append(check)
            if check["status"] == "FAIL":
                overall = "FAIL"

        return {
            "contract_id": policy.get("contract_id", "unknown"),
            "guard_version": self.guard_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "policy_fingerprint": self._get_policy_fingerprint(),
            "checks": checks,
            "overall": overall
        }

    def boundary(self) -> dict:
        """BOUNDARY: Git delta within allowlist + protected"""
        return self.check_boundary()

    def close(self) -> dict:
        """CLOSE: boundary → test → boundary + evidence"""
        results = {
            "contract_id": self._get_policy().get("contract_id", "unknown"),
            "guard_version": self.guard_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "policy_fingerprint": self._get_policy_fingerprint(),
            "checks": [],
            "overall": "PASS"
        }

        # 1. Boundary before tests
        boundary_before = self.check_boundary()
        if boundary_before["overall"] == "FAIL":
            results["checks"].append({
                "name": "BOUNDARY_BEFORE_TESTS",
                "status": "FAIL",
                "details": boundary_before.get("violations", [])
            })
            results["overall"] = "FAIL"
            self._save_evidence(results)
            return results
        results["checks"].append({
            "name": "BOUNDARY_BEFORE_TESTS",
            "status": "PASS",
            "changed_files": boundary_before.get("changed_files", [])
        })

        # 2. Run tests
        test_result = self.run_tests()
        if test_result["overall"] == "FAIL":
            results["checks"].append({
                "name": "MANDATORY_TESTS",
                "status": "FAIL",
                "details": {"exit_code": test_result.get("exit_code"), "message": test_result.get("message")}
            })
            results["overall"] = "FAIL"
        else:
            results["checks"].append({
                "name": "MANDATORY_TESTS",
                "status": "PASS",
                "database": test_result.get("database")
            })

        # 3. Boundary after tests
        boundary_after = self.check_boundary()
        if boundary_after["overall"] == "FAIL":
            results["checks"].append({
                "name": "BOUNDARY_AFTER_TESTS",
                "status": "FAIL",
                "details": boundary_after.get("violations", [])
            })
            results["overall"] = "FAIL"
        else:
            results["checks"].append({
                "name": "BOUNDARY_AFTER_TESTS",
                "status": "PASS",
                "changed_files": boundary_after.get("changed_files", [])
            })

        # 4. Evidence
        evidence_path = self._save_evidence(results)
        results["evidence_path"] = str(evidence_path)

        return results


# ========== CLI ==========

def main():
    parser = argparse.ArgumentParser(description="Contract Guard v0.1")
    parser.add_argument("command", choices=["preflight", "boundary", "close"])
    parser.add_argument("--cc-path", required=True, help="Path to approved CC file")
    parser.add_argument("--baseline", required=True, help="Execution Baseline commit")

    args = parser.parse_args()

    try:
        guard = ContractGuard(args.cc_path, args.baseline)
    except ContractGuardError as e:
        print(json.dumps({"overall": "ERROR", "message": str(e)}, indent=2))
        sys.exit(1)

    if args.command == "preflight":
        result = guard.preflight()
    elif args.command == "boundary":
        result = guard.boundary()
    elif args.command == "close":
        result = guard.close()
    else:
        print(json.dumps({"overall": "ERROR", "message": f"Unknown command: {args.command}"}, indent=2))
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("overall") == "PASS" else 1)


if __name__ == "__main__":
    main()
```

---

## 三、Python 单元测试（完整版本）

**文件：`tests/guard/test_guard.py`**

> 说明：Guard 自身测试必须使用独立临时 Git 仓库和 fake Odoo runner，不连接真实数据库。  
> 负向测试通过返回码和 JSON 结果做断言，不依赖 Shell `set -e`。

````python
#!/usr/bin/env python3
"""
Contract Guard v0.1 self-tests.

目标：
1. PRE-FLIGHT 正常/异常路径；
2. BOUNDARY 对 modified/created/deleted/untracked/protected/rename/type-change 的判定；
3. CLOSE 对 mandatory test PASS/FAIL 的判定；
4. 证明测试执行后出现越界文件时，BOUNDARY_AFTER_TESTS 会 BLOCK；
5. 整个测试不访问真实 Odoo / PostgreSQL。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestContractGuard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="contract-guard-test-")
        cls.repo_root = Path(cls.test_dir)

        def run(*args, **kwargs):
            return subprocess.run(
                list(args),
                cwd=cls.repo_root,
                check=True,
                capture_output=True,
                text=True,
                **kwargs,
            )

        run("git", "init")
        run("git", "config", "user.email", "guard-test@example.invalid")
        run("git", "config", "user.name", "Contract Guard Test")

        # 基础目录
        (cls.repo_root / ".guard").mkdir()
        (cls.repo_root / "docs/context/coding").mkdir(parents=True)
        (cls.repo_root / "src/protected").mkdir(parents=True)
        (cls.repo_root / "tests/fake").mkdir(parents=True)

        # 复制被测 Guard
        guard_src = (
            Path(__file__).resolve().parents[2]
            / ".guard"
            / "contract_guard.py"
        )
        if not guard_src.exists():
            raise unittest.SkipTest(
                f"contract_guard.py not found: {guard_src}"
            )
        shutil.copy2(
            guard_src,
            cls.repo_root / ".guard" / "contract_guard.py"
        )

        # Guard evidence 是运行产物，不参与 Boundary
        (cls.repo_root / ".gitignore").write_text(
            ".guard/evidence/
",
            encoding="utf-8",
        )

        # 基础 tracked 文件
        (cls.repo_root / "src/test.py").write_text(
            "VALUE = 1
",
            encoding="utf-8",
        )
        (cls.repo_root / "src/other.py").write_text(
            "OTHER = 1
",
            encoding="utf-8",
        )
        (cls.repo_root / "src/protected/secret.py").write_text(
            "SECRET = 1
",
            encoding="utf-8",
        )

        # fake Odoo runner：
        # FAKE_ODOO_MODE=pass       -> exit 0
        # FAKE_ODOO_MODE=fail       -> exit 9
        # FAKE_ODOO_MODE=write_bad  -> 创建未授权文件后 exit 0
        fake_odoo = cls.repo_root / "tests/fake/fake_odoo.py"
        fake_odoo.write_text(
            """#!/usr/bin/env python3
import os
import pathlib
import sys

mode = os.environ.get("FAKE_ODOO_MODE", "pass")

if mode == "write_bad":
    pathlib.Path("runtime_output.tmp").write_text(
        "created by fake test runner\n",
        encoding="utf-8",
    )
    sys.exit(0)

if mode == "fail":
    print("simulated mandatory test failure", file=sys.stderr)
    sys.exit(9)

print("simulated mandatory tests passed")
sys.exit(0)
""",
            encoding="utf-8",
        )

        # Enforcement Block。
        # runner.python = 当前 Python
        # runner.odoo_bin = fake runner
        cc = f"""# TEST CC

<!-- CONTRACT_ENFORCEMENT_START -->
```yaml
enforcement:
  schema_version: "0.1"
  contract_id: TEST-001
  status: approved

  allowed_modify:
    - src/test.py

  allowed_create:
    - src/new.py

  allowed_delete: []

  protected:
    - src/protected/**

  tests:
    database: guard_fake_db
    odoo_config: odoo.conf
    addons_path:
      - addons
    module: fake_module
    test_tags:
      - /fake_module
    timeout_seconds: 30
    runner:
      python: {json.dumps(sys.executable)}
      odoo_bin: tests/fake/fake_odoo.py
```
<!-- CONTRACT_ENFORCEMENT_END -->
"""
        cls.cc_path = (
            "docs/context/coding/"
            "Coding_Contract_TEST-001_approved.md"
        )
        (cls.repo_root / cls.cc_path).write_text(
            cc,
            encoding="utf-8",
        )

        run("git", "add", ".")
        run("git", "commit", "-m", "test: establish execution baseline")

        cls.baseline = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cls.repo_root,
            text=True,
        ).strip()

        cls.guard_path = (
            cls.repo_root / ".guard" / "contract_guard.py"
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        self._reset_repo()

    # ---------- helpers ----------

    def _git(self, *args, check=True):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=check,
            capture_output=True,
            text=True,
        )

    def _reset_repo(self):
        self._git("reset", "--hard", self.baseline)
        self._git("clean", "-fd")
        evidence_dir = self.repo_root / ".guard/evidence"
        if evidence_dir.exists():
            shutil.rmtree(evidence_dir)

    def _run_guard(self, command, *, env=None, baseline=None):
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        cmd = [
            sys.executable,
            str(self.guard_path),
            command,
            "--cc-path",
            self.cc_path,
            "--baseline",
            baseline or self.baseline,
        ]

        completed = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            env=merged_env,
        )

        # Guard 使用 indent=2 输出多行 JSON，必须解析整个 stdout，
        # 不能只取最后一行。
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                "Guard did not emit valid JSON.
"
                f"exit={completed.returncode}
"
                f"stdout={completed.stdout}
"
                f"stderr={completed.stderr}
"
                f"error={exc}"
            )

        payload["_exit_code"] = completed.returncode
        payload["_stderr"] = completed.stderr
        return payload

    @staticmethod
    def _check(result, name):
        return next(
            (
                item
                for item in result.get("checks", [])
                if item.get("name") == name
            ),
            {},
        )

    # ---------- PRE-FLIGHT ----------

    def test_preflight_pass(self):
        result = self._run_guard("preflight")
        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(result["_exit_code"], 0)
        self.assertEqual(
            self._check(result, "EXECUTION_BASELINE").get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(result, "WORKTREE_CLEAN").get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(result, "CC_STATUS").get("status"),
            "PASS",
        )

    def test_preflight_blocks_dirty_worktree(self):
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        result = self._run_guard("preflight")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        self.assertEqual(
            self._check(result, "WORKTREE_CLEAN").get("status"),
            "FAIL",
        )

    def test_preflight_blocks_head_mismatch(self):
        (self.repo_root / "src/other.py").write_text(
            "OTHER = 2
",
            encoding="utf-8",
        )
        self._git("add", "src/other.py")
        self._git("commit", "-m", "test: move head past baseline")

        result = self._run_guard("preflight")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        self.assertEqual(
            self._check(result, "EXECUTION_BASELINE").get("status"),
            "FAIL",
        )

    def test_preflight_blocks_unresolvable_baseline(self):
        result = self._run_guard(
            "preflight",
            baseline="definitely-not-a-git-revision",
        )
        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)

    # ---------- BOUNDARY ----------

    def test_boundary_passes_authorized_modify(self):
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(result["_exit_code"], 0)

    def test_boundary_passes_authorized_create(self):
        (self.repo_root / "src/new.py").write_text(
            "NEW = 1
",
            encoding="utf-8",
        )

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(result["_exit_code"], 0)

    def test_boundary_blocks_unauthorized_modify(self):
        (self.repo_root / "src/other.py").write_text(
            "OTHER = 99
",
            encoding="utf-8",
        )

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }
        self.assertIn("UNAUTHORIZED_MODIFY", reasons)

    def test_boundary_blocks_unauthorized_untracked_create(self):
        (self.repo_root / "src/bad.py").write_text(
            "BAD = 1
",
            encoding="utf-8",
        )

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }
        self.assertIn("UNAUTHORIZED_CREATE", reasons)

    def test_boundary_blocks_protected_modify(self):
        (self.repo_root / "src/protected/secret.py").write_text(
            "SECRET = 999
",
            encoding="utf-8",
        )

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }
        self.assertIn("PROTECTED_MODIFY", reasons)

    def test_boundary_blocks_delete(self):
        (self.repo_root / "src/test.py").unlink()

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }
        self.assertIn("UNAUTHORIZED_DELETE", reasons)

    def test_boundary_blocks_rename(self):
        self._git("mv", "src/test.py", "src/test_renamed.py")

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)

        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }

        # 若 Git 识别 rename，则应为 RENAME_NOT_ALLOWED；
        # 若当前 Git 配置将其表示为 delete+create，也必须 FAIL。
        self.assertTrue(
            "RENAME_NOT_ALLOWED" in reasons
            or "UNAUTHORIZED_DELETE" in reasons
            or "UNAUTHORIZED_CREATE" in reasons
        )

    def test_boundary_blocks_type_change(self):
        target = self.repo_root / "src/test.py"
        target.unlink()
        target.symlink_to("other.py")

        result = self._run_guard("boundary")

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)

        reasons = {
            v.get("reason") for v in result.get("violations", [])
        }
        self.assertIn("TYPE_CHANGE_NOT_ALLOWED", reasons)

    # ---------- CLOSE ----------

    def test_close_passes_with_fake_mandatory_tests(self):
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        result = self._run_guard(
            "close",
            env={"FAKE_ODOO_MODE": "pass"},
        )

        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(result["_exit_code"], 0)
        self.assertEqual(
            self._check(
                result,
                "BOUNDARY_BEFORE_TESTS",
            ).get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(
                result,
                "MANDATORY_TESTS",
            ).get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(
                result,
                "BOUNDARY_AFTER_TESTS",
            ).get("status"),
            "PASS",
        )

        evidence_dir = self.repo_root / ".guard/evidence"
        self.assertTrue(evidence_dir.exists())
        self.assertTrue(list(evidence_dir.glob("*.json")))

    def test_close_blocks_mandatory_test_failure(self):
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        result = self._run_guard(
            "close",
            env={"FAKE_ODOO_MODE": "fail"},
        )

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)
        self.assertEqual(
            self._check(
                result,
                "MANDATORY_TESTS",
            ).get("status"),
            "FAIL",
        )

    def test_close_blocks_file_created_by_test_runner(self):
        # 测试前只有合法修改，因此第一次 Boundary 必须 PASS。
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        result = self._run_guard(
            "close",
            env={"FAKE_ODOO_MODE": "write_bad"},
        )

        self.assertEqual(result["overall"], "FAIL")
        self.assertEqual(result["_exit_code"], 1)

        self.assertEqual(
            self._check(
                result,
                "BOUNDARY_BEFORE_TESTS",
            ).get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(
                result,
                "MANDATORY_TESTS",
            ).get("status"),
            "PASS",
        )
        self.assertEqual(
            self._check(
                result,
                "BOUNDARY_AFTER_TESTS",
            ).get("status"),
            "FAIL",
        )

        self.assertTrue(
            (self.repo_root / "runtime_output.tmp").exists()
        )

    def test_evidence_does_not_pollute_next_boundary(self):
        (self.repo_root / "src/test.py").write_text(
            "VALUE = 2
",
            encoding="utf-8",
        )

        close_result = self._run_guard(
            "close",
            env={"FAKE_ODOO_MODE": "pass"},
        )
        self.assertEqual(close_result["overall"], "PASS")

        boundary_result = self._run_guard("boundary")
        self.assertEqual(boundary_result["overall"], "PASS")
        self.assertEqual(boundary_result["_exit_code"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
````

---

## 四、运行 Guard 自身测试

```bash
# 推荐
python -m pytest tests/guard/test_guard.py -v

# 不安装 pytest 时
python tests/guard/test_guard.py
```

**验收条件：以上测试必须实际运行并全部通过。未运行不得写 PASS。**


## 五、Execution Baseline 建立流程

```bash
# 1. 确保代码处于要开工的状态
git status --porcelain  # 必须为空

# 2. 创建/更新 CC，添加 Enforcement Block
vim docs/context/coding/Coding_Contract_CC-01_warehouse_vas_v1.0_approved.md

# 3. 提交 CC
git add docs/context/coding/Coding_Contract_CC-01_warehouse_vas_v1.0_approved.md
git commit -m "docs: add enforcement block for CC-01"

# 4. 记录 Execution Baseline
BASELINE=$(git rev-parse HEAD)
echo "Execution Baseline: $BASELINE"

# 5. Agent 使用此 baseline
python .guard/contract_guard.py preflight --cc-path docs/context/coding/Coding_Contract_CC-01_warehouse_vas_v1.0_approved.md --baseline $BASELINE
```