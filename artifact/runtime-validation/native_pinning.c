#include <jni.h>
/* A Java callback sleeps while a JNI frame remains on the stack. No external I/O. */
JNIEXPORT void JNICALL Java_RuntimeSmoke_nativeCallback(JNIEnv *env, jclass clazz) {
    jmethodID callback = (*env)->GetStaticMethodID(env, clazz, "sleepCallback", "()V");
    if (callback != NULL) (*env)->CallStaticVoidMethod(env, clazz, callback);
}
