from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the popup.html file directly
        # We need to use absolute path
        cwd = os.getcwd()
        url = f"file://{cwd}/src/popup.html"

        print(f"Loading {url}")

        # We need to mock chrome API because popup.js uses it immediately
        # and would crash/stop execution if not present.
        page.add_init_script("""
            window.chrome = {
                storage: {
                    sync: {
                        get: (keys) => Promise.resolve({ accessToken: 'mock-token' })
                    },
                    local: {
                        get: (keys) => Promise.resolve({
                            pushes: [],
                            sentMessages: [],
                            showQuickShare: true,
                            notificationMirroring: false,
                            defaultTab: 'push',
                            colorMode: 'light'
                        })
                    },
                    onChanged: {
                        addListener: () => {}
                    }
                },
                runtime: {
                    sendMessage: (msg, callback) => {
                        if (msg.type === 'get_status') {
                            if (callback) callback({ status: 'connected' });
                        }
                    },
                    openOptionsPage: () => {}
                },
                tabs: {
                    query: () => Promise.resolve([{ url: 'https://example.com' }]),
                    create: () => {}
                },
                windows: {
                    create: () => {}
                }
            };

            // Mock CustomI18n if it's missing (though it should be loaded from i18n.js if present)
            // But i18n.js relies on chrome.i18n which we need to mock or it will fail
            window.chrome.i18n = {
                getMessage: (key) => key
            };
        """)

        page.goto(url)

        # Wait for the button to be visible
        page.wait_for_selector("#sendUrlButton")

        # Take screenshot
        page.screenshot(path="verification/popup_screenshot.png")

        browser.close()

if __name__ == "__main__":
    run()
