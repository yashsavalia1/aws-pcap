import Image from "next/image";
import logo from "../assets/logo-circle.png";
import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="sidebar h-full sidebar-fixed-left justify-start">
      <section className="sidebar-title items-center p-4">
        <div className="mr-4">
          <Image src={logo.src} height={50} width={50} alt="" />
        </div>
        <div className="flex flex-col">
          <span>AWS Packet Capturing</span>
          <span className="text-xs font-normal text-content2">Group 4</span>
        </div>
      </section>
      <hr className="mx-4" />
      <section className="sidebar-content h-fit min-h-[20rem] overflow-visible">
        <nav className="menu rounded-md">
          <section className="menu-section px-4">
            <ul className="menu-items">
              <Link href="./">
                <li className="menu-item">Home</li>
              </Link>
              <Link href="./latency-analytics">
                <li className="menu-item">Latency Analytics</li>
              </Link>
              <Link href="./packet-explorer">
                <li className="menu-item">Packet Explorer</li>
              </Link>

              <Link href="./order-explorer">
                <li className="menu-item">Order Explorer</li>
              </Link>
              {/* <li className="menu-item">
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
              </li> */}
            </ul>
          </section>
        </nav>
      </section>
    </aside>
  );
}
