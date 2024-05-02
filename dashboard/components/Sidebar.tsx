import Image from "next/image";
import logo from "../assets/logo-circle.png";

export default function Sidebar() {
  return (
    <aside className="sidebar h-full sidebar-fixed-left justify-start">
      <section className="sidebar-title items-center p-4">
        <div className="mr-4">
          <Image src={logo.src} height={50} width={50} alt=""/>
        </div>
        <div className="flex flex-col">
          <span>AWS Packet Capturing</span>
          <span className="text-xs font-normal text-content2">Group 4</span>
        </div>
      </section>
      <section className="sidebar-content h-fit min-h-[20rem] overflow-visible">
        <nav className="menu rounded-md">
          <section className="menu-section px-4">
            <ul className="menu-items">
              <li className="menu-item">
                <span>General</span>
              </li>

              <li className="menu-item">
                <span>Teams</span>
              </li>
              <li className="menu-item">
                <span>Billing</span>
              </li>
              <li>
                <input type="checkbox" id="menu-1" className="menu-toggle" />
                <label className="menu-item justify-between" htmlFor="menu-1">
                  <div className="flex gap-2">
                    <span>Account</span>
                  </div>

                  <span className="menu-icon">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                </label>

                <div className="menu-item-collapse">
                  <div className="min-h-0">
                    <label className="menu-item-disabled menu-item ml-6">
                      Accounts
                    </label>
                    <label className="menu-item ml-6">Billing</label>
                    <label className="menu-item ml-6">Security</label>
                    <label className="menu-item ml-6">Notifications</label>
                    <label className="menu-item ml-6">Integrations</label>
                  </div>
                </div>
              </li>
            </ul>
          </section>
        </nav>
      </section>
      <section className="sidebar-footer h-full justify-end bg-gray-2 pt-2">
        <div className="divider my-0"></div>
        <div className="dropdown z-50 flex h-fit w-full cursor-pointer hover:bg-gray-4">
          <label
            className="whites mx-2 flex h-fit w-full cursor-pointer p-0 hover:bg-gray-4"
            tabIndex={0}
          >
            <div className="flex flex-row gap-4 p-4">
              <div className="avatar avatar-md">
                <img src="https://i.pravatar.cc/150?img=30" alt="avatar" />
              </div>

              <div className="flex flex-col">
                <span>Sandra Marx</span>
                <span className="text-xs font-normal text-content2">
                  sandra
                </span>
              </div>
            </div>
          </label>
          <div className="dropdown-menu dropdown-menu-right-top ml-2">
            <a className="dropdown-item text-sm">Profile</a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Account settings
            </a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Change email
            </a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Subscriptions
            </a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Change password
            </a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Refer a friend
            </a>
            <a tabIndex={-1} className="dropdown-item text-sm">
              Settings
            </a>
          </div>
        </div>
      </section>
    </aside>
  );
}
