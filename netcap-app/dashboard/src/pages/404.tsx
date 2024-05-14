
export default function NotFound() {
    return (
        <div className="flex flex-col w-screen h-screen justify-center items-center">
            <h1 className="text-2xl font-bold">404</h1>
            <p className="text-lg">Page not found</p>
            <a href="/" className="btn mt-5 btn-primary">Go to Home</a>
        </div>
    );
}