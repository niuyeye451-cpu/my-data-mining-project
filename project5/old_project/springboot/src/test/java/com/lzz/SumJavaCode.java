package com.lzz;


import java.io.*;

public class SumJavaCode {

    static long normalLines = 0; // 空行
    static long commentLines = 0; // 注释行
    static long whiteLines = 0; // 代码行

    public static void main(String[] args) {

        SumJavaCode sjc = new SumJavaCode();
        File f = new File("D:\\lzz\\lzz_project_solrj\\vue\\src"); // 正式目录
//        File f = new File("D:\\Lucene\\lucene资料\\资源\\案例代码\\luceneDemo\\src"); // 早期测试目录
        System.out.println(f.getName());
        sjc.treeFile(f);
        System.out.println("空行：" + whiteLines);
        System.out.println("注释行：" + commentLines);
        System.out.println("代码行：" + normalLines);
    }

    /**
     * 　　* 查找出一个目录下所有的.java ,.xml，.vue，.js，.html 文件
     * 　　*
     * 　　* @param f 要查找的目录
     *
     */
    private void treeFile(File f) {
        File[] childs = f.listFiles();
        for (int i = 0; i < childs.length; i++) {
            if (!childs[i].isDirectory()) {
                if (childs[i].getName().matches(".*\\.java$") || childs[i].getName().matches(".*\\.xml$") ||
                        childs[i].getName().matches(".*\\.vue$") || childs[i].getName().matches(".*\\.js$")||
                        childs[i].getName().matches(".*\\.html$")) {
                    System.out.println(childs[i].getName());
                    sumCode(childs[i]);
                }
            } else {
                treeFile(childs[i]);
            }
        }
    }

    /**
     * 　　* 计算一个.java文件中的代码行，空行，注释行
     * 　　*
     * 　　* @param file
     * 　　* 要计算的.java文件
     *
     */
    private void sumCode(File file) {
        BufferedReader br = null;
        boolean comment = false;
        try {
            br = new BufferedReader(new FileReader(file));
            String line = "";
            try {
                while ((line = br.readLine()) != null) {
                    line = line.trim();
                    if (line.matches("^[\\s&&[^\\n]]*$")) {
                        whiteLines++;
                    } else if (line.startsWith("/*") && !line.endsWith("*/")) {
                        commentLines++;
                        comment = true;
                    } else if (comment) {
                        commentLines++;
                        if (line.endsWith("*/")) {
                            comment = false;
                        }
                    } else if (line.startsWith("//")) {
                        commentLines++;
                    } else {
                        normalLines++;
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        } catch (
                FileNotFoundException e) {
            e.printStackTrace();
        } finally {
            if (br != null) {
                try {
                    br.close();
                    br = null;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
