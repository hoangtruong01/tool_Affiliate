declare module 'cookie-cutter' {
    const cookieCutter: {
        get: (key: string) => string | undefined;
        set: (key: string, value: string, options?: any) => void;
    };
    export default cookieCutter;
}
