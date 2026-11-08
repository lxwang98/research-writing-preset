// 纯声明式 bundle：DSH 只读取 `dsh.bundle.patch` 指向的 cordis.patch.yml。
// 保留空入口模块，方便 `resolve('<pkg>/package.json')` 与常规 ESM 解析走同一条路径。
export {}
