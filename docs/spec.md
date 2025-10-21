# 🌐 SocialCLI – CLI Framework for Social Scheduling
**Version:** 1.0  
**Author:** Stefano Maestri  
**Last Updated:** October 20, 2025  

---

## 🧭 Vision

**SocialCLI** is a command-line framework for posting, commenting, and scheduling content across multiple social platforms (LinkedIn, X, Threads, Bluesky, Mastodon, etc.).  
Its goal is to provide a modular, open, and scriptable architecture that allows users to:
- manage multiple social platforms from a single CLI tool,  
- abstract differences between APIs and authentication models,  
- enable future extensions via plugins or provider drivers.  

The **first implementation** will be the **LinkedIn Provider** module, serving as the reference architecture.

---

## 🎯 Main Objectives

| # | Objective | Description | Priority |
|---|------------|-------------|-----------|
| 1 | Generic CLI Framework | Common architecture for all social platforms | 🟥 High |
| 2 | Provider Abstraction Layer | Unified interface for posts, comments, and media | 🟥 High |
| 3 | LinkedIn Implementation | First integrated platform (MVP) | 🟥 High |
| 4 | Local Scheduler | Cross-social post scheduling | 🟥 High |
| 5 | Multi-account Config | Manage credentials and multiple tokens | 🟧 Medium |
| 6 | Plugin Architecture | Future support for additional social platforms | 🟧 Medium |
| 7 | CLI Dashboard (status, logs) | Display post results and queues | 🟩 Low |

---

## ⚙️ Architecture

### 1. **Core Layer**
Handles:
- CLI (common commands)
- Local scheduler (queue)
- Storage and logging management
- Configuration (tokens, profiles, preferences)

### 2. **Provider Layer**
Generic interface to interact with each social network.

```python
class SocialProvider(ABC):
    @abstractmethod
    def login(self): ...
    @abstractmethod
    def post(self, content: str, **kwargs): ...
    @abstractmethod
    def comment(self, target_id: str, text: str): ...
    @abstractmethod
    def repost(self, target_id: str, text: Optional[str] = None): ...
```

### 3. **Adapters (Plugins)**
Each social platform implements its own adapter that realizes the interface.  
Examples:
- `LinkedInProvider` (MVP)
- `XProvider`
- `BlueskyProvider`
- `ThreadsProvider`

### 4. **CLI Layer**
Exposes the commands:
```
socialcli login [--provider linkedin]
socialcli post --file post.md --provider linkedin
socialcli comment --provider linkedin --target-id ...
socialcli queue --list
```

---

## 🧱 MVP Implementation: LinkedIn Provider

The **LinkedInProvider** module implements the APIs described in the previous PRD.

### Supported Scopes
- `w_member_social`, `r_liteprofile`
- `w_organization_social`, `rw_organization_admin` (for pages)
- Local scheduler via SQLite

### Used Endpoints
- `/rest/posts`
- `/rest/comments`
- `/rest/assets?action=registerUpload`

### Example Config File
```yaml
providers:
  linkedin:
    client_id: <CLIENT_ID>
    client_secret: <CLIENT_SECRET>
    access_token: <ACCESS_TOKEN>
    refresh_token: <REFRESH_TOKEN>
  default_provider: linkedin
```

---

## 💡 Future Architecture: Provider Plugin System

Each new social platform will be added as an independent Python module:

```
socialcli/
 ├── core/
 │   ├── cli.py
 │   ├── scheduler.py
 │   └── storage.py
 ├── providers/
 │   ├── linkedin/
 │   │   ├── provider.py
 │   │   └── auth.py
 │   ├── x/
 │   ├── bluesky/
 │   ├── threads/
 │   └── __init__.py
 └── utils/
```

Each provider must export:
```python
PROVIDER_NAME = "linkedin"

def get_provider():
    return LinkedInProvider()
```

The core CLI dynamically loads registered providers via entry points or directory scanning.

---

## 🧠 Scheduler and Queue

Common system across all providers:
- SQLite `scheduled_posts` with fields:
  - `id`
  - `provider`
  - `author`
  - `file_path`
  - `publish_at`
  - `status`
- A periodic task checks jobs and calls `provider.post(content)` at the scheduled time.

---

## 🧩 Post Files

### `.md` / `.txt` Format
All providers accept soft Markdown text.

Example:
```markdown
💬 Agents, AI, and Humility

Karpathy’s latest interview sparks an important point: tools evolve, but humility must remain.

#AI #AgenticAI
```

CLI:
```bash
socialcli post --file post.md --provider linkedin
```

### Optional Header (front matter)
```markdown
---
title: Karpathy and Developers’ Humility
tags: [AI, Agents]
provider: linkedin
schedule: 2025-10-21T09:00
---
```

---

## 🔐 Security and Token Management

Each provider handles its own tokens in `~/.socialcli/config.yaml`.  
The core provides caching, automatic refresh, and secure rotation functions.

---

## 🚀 Extensibility (Phase 2)

| Social | Authentication Type | Planned Status |
|--------|----------------------|----------------|
| **LinkedIn** | OAuth 2.0 3-legged | ✅ MVP |
| **X (Twitter)** | OAuth 2.0 Bearer / v2 API | 🔜 |
| **Bluesky** | Basic Auth + ATProto API | 🔜 |
| **Threads** | Graph API (Meta) | 🔜 |
| **Mastodon** | OAuth 2.0 | 🔜 |

---

## 📈 Success Metrics

| KPI | Target |
|------|--------|
| Cross-provider post time | < 5 s |
| Core modularity | ≤ 500 LOC |
| Average provider setup time | < 2 min |
| Successful post rate | > 98% |
| Time to add a new provider | < 2h for basic implementation |

---

## 🧱 Licensing and Distribution

- **License:** MIT  
- **Repository:** Public GitHub  
- **Package:** `pip install socialcli`  
- **Config:** `~/.socialcli/config.yaml`  

---

## 🧭 Roadmap

| Phase | Goal | Deliverable |
|------|-------|--------------|
| 1️⃣ | MVP LinkedIn | Core framework + LinkedIn provider |
| 2️⃣ | Plugin system | Multi-provider support |
| 3️⃣ | X and Bluesky | Add-on providers |
| 4️⃣ | Web dashboard (optional) | Post monitoring UI |
| 5️⃣ | Notion / Git integration | Direct post imports |

---

## ✅ Summary

**SocialCLI** is an extensible CLI framework for managing social content.  
The first milestone implements **LinkedIn** as the reference provider, but the architecture allows easy addition of other platforms.

**Design Pillars:**
- modularity  
- simplicity  
- future extensibility  
- open-source transparency  

> “Start with LinkedIn. Scale to the social web.” 🌍